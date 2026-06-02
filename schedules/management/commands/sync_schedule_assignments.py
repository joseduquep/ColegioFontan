"""
Reconcilia Schedule y Block.students en la base de datos desplegada.

Uso:
  python manage.py sync_schedule_assignments
  python manage.py sync_schedule_assignments --dry-run
  python manage.py sync_schedule_assignments --verify-only
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Exists, OuterRef

from schedules.models import Schedule
from workshops.models import Block


def batched(qs, batch_size=400):
    """Paginacion por PK sin cursores server-side (compatible con Neon/pooler)."""
    last_pk = 0
    model = qs.model
    pk_name = model._meta.pk.name
    while True:
        filter_kw = {f'{pk_name}__gt': last_pk}
        batch = list(qs.filter(**filter_kw).order_by(pk_name)[:batch_size])
        if not batch:
            break
        yield from batch
        last_pk = getattr(batch[-1], pk_name)


class Command(BaseCommand):
    help = "Sincroniza Schedule con Block.students y corrige asignaciones duplicadas."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra que cambios haria, sin escribir en la BD.',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Lista cada cambio (puede fallar en consolas Windows sin UTF-8).',
        )
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Solo verifica consistencia, sin modificar datos.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        verify_only = options['verify_only']
        through = Block.students.through

        if verify_only:
            self._print_verification(through)
            return

        stats = {
            'm2m_added': 0,
            'm2m_removed': 0,
            'schedules_removed_dup': 0,
            'slots_cleared_extra_m2m': 0,
        }

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run: no se guardaran cambios.'))

        # --- Paso 1: Schedule sin M2M en su bloque ---
        self.stdout.write('Paso 1/4: agregar M2M faltantes segun Schedule...')
        in_m2m = through.objects.filter(
            block_id=OuterRef('block_id'),
            student_id=OuterRef('student_id'),
        )
        missing_qs = (
            Schedule.objects
            .annotate(has_m2m=Exists(in_m2m))
            .filter(has_m2m=False)
            .only('schedule_id', 'block_id', 'student_id')
        )
        missing_list = list(missing_qs)
        stats['m2m_added'] = len(missing_list)

        if not dry_run and missing_list:
            links = [
                through(block_id=s.block_id, student_id=s.student_id)
                for s in missing_list
            ]
            through.objects.bulk_create(links, ignore_conflicts=True, batch_size=500)

        if verbose and missing_list:
            for s in missing_list[:20]:
                self.stdout.write(
                    f"  + M2M: student_id={s.student_id} -> block_id={s.block_id}"
                )

        # --- Paso 2: Schedule duplicados en el mismo slot ---
        self.stdout.write('Paso 2/4: eliminar Schedule duplicados...')
        dup_slots = (
            Schedule.objects
            .values('student_id', 'block__day', 'block__block_number', 'block__type')
            .annotate(c=Count('schedule_id'))
            .filter(c__gt=1)
        )
        for row in dup_slots:
            schedules = list(
                Schedule.objects
                .filter(
                    student_id=row['student_id'],
                    block__day=row['block__day'],
                    block__block_number=row['block__block_number'],
                    block__type=row['block__type'],
                )
                .order_by('schedule_id')
            )
            for extra in schedules[1:]:
                stats['schedules_removed_dup'] += 1
                if verbose:
                    self.stdout.write(
                        f"  - Schedule duplicado id={extra.schedule_id}"
                    )
                if not dry_run:
                    extra.delete()

        # --- Paso 3: M2M sin Schedule en ese slot ---
        self.stdout.write('Paso 3/4: quitar M2M huerfanos...')
        orphan_pairs = []
        link_qs = through.objects.select_related('block').all()
        for link in batched(link_qs):
            block = link.block
            if not Schedule.objects.filter(
                student_id=link.student_id,
                block__day=block.day,
                block__block_number=block.block_number,
                block__type=block.type,
            ).exists():
                orphan_pairs.append((link.block_id, link.student_id))
                stats['m2m_removed'] += 1
                if verbose:
                    self.stdout.write(
                        f"  - M2M huerfano: student_id={link.student_id} "
                        f"block_id={link.block_id}"
                    )

        if not dry_run and orphan_pairs:
            for block_id, student_id in orphan_pairs:
                through.objects.filter(
                    block_id=block_id,
                    student_id=student_id,
                ).delete()

        # --- Paso 4: varios bloques M2M en el mismo slot ---
        self.stdout.write('Paso 4/4: quitar M2M en bloque equivocado...')
        from students.models import Student

        student_qs = Student.objects.all().only('student_id')
        for student in batched(student_qs):
            blocks = list(
                Block.objects.filter(students=student).only(
                    'block_id', 'day', 'block_number', 'type'
                )
            )
            slots = {}
            for b in blocks:
                key = (b.day, b.block_number, b.type)
                slots.setdefault(key, []).append(b)

            for (day, block_number, block_type), blist in slots.items():
                if len(blist) <= 1:
                    continue
                schedule = Schedule.objects.filter(
                    student=student,
                    block__day=day,
                    block__block_number=block_number,
                    block__type=block_type,
                ).only('block_id').first()
                canonical_id = schedule.block_id if schedule else None
                for b in blist:
                    if b.block_id == canonical_id:
                        continue
                    stats['slots_cleared_extra_m2m'] += 1
                    if verbose:
                        self.stdout.write(
                            f"  - M2M extra: student_id={student.student_id} "
                            f"block_id={b.block_id} canonico={canonical_id}"
                        )
                    if not dry_run:
                        through.objects.filter(
                            block_id=b.block_id,
                            student_id=student.student_id,
                        ).delete()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Resumen de cambios:'))
        for key, val in stats.items():
            self.stdout.write(f'  {key}: {val}')
        if dry_run:
            self.stdout.write(self.style.WARNING('Ejecuta sin --dry-run para aplicar.'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Verificacion post-sync:'))
        issues = self._collect_issues(through)
        total_schedules = Schedule.objects.count()
        self.stdout.write(f'  total_schedule_rows: {total_schedules}')
        if any(issues.values()):
            for name, count in issues.items():
                self.stdout.write(self.style.ERROR(f'  {name}: {count}'))
            self.stdout.write(self.style.ERROR(
                'Quedan inconsistencias; vuelve a ejecutar el comando.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                '  OK: Schedule y Block.students estan sincronizados.'
            ))

    def _collect_issues(self, through):
        in_m2m = through.objects.filter(
            block_id=OuterRef('block_id'),
            student_id=OuterRef('student_id'),
        )
        missing_m2m = Schedule.objects.annotate(
            has_m2m=Exists(in_m2m)
        ).filter(has_m2m=False).count()

        orphan_m2m = 0
        wrong_m2m = 0
        link_qs = through.objects.select_related('block').all()
        for link in batched(link_qs):
            block = link.block
            schedule = Schedule.objects.filter(
                student_id=link.student_id,
                block__day=block.day,
                block__block_number=block.block_number,
                block__type=block.type,
            ).only('block_id').first()
            if not schedule:
                orphan_m2m += 1
            elif link.block_id != schedule.block_id:
                wrong_m2m += 1

        dup_schedules = (
            Schedule.objects
            .values('student_id', 'block__day', 'block__block_number', 'block__type')
            .annotate(c=Count('schedule_id'))
            .filter(c__gt=1)
            .count()
        )

        return {
            'missing_m2m': missing_m2m,
            'orphan_m2m': orphan_m2m,
            'wrong_m2m_slot': wrong_m2m,
            'duplicate_schedules': dup_schedules,
        }

    def _print_verification(self, through):
        self.stdout.write('Verificacion (solo lectura):')
        issues = self._collect_issues(through)
        total_schedules = Schedule.objects.count()
        self.stdout.write(f'  total_schedule_rows: {total_schedules}')
        if any(issues.values()):
            for name, count in issues.items():
                self.stdout.write(self.style.WARNING(f'  {name}: {count}'))
        else:
            self.stdout.write(self.style.SUCCESS('  OK: sin inconsistencias detectadas.'))
