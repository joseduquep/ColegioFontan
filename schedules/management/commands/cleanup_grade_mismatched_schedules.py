"""
Desvincula a los estudiantes de bloques (Schedule + Block.students) que ya no
correspondan a su nivel academico actual segun su grado (por ejemplo,
estudiantes que pasaron de grado 5 a 6 y quedaron con bloques de primaria).

No borra historial de asistencia (Attendance).

Uso:
  python manage.py cleanup_grade_mismatched_schedules --dry-run
  python manage.py cleanup_grade_mismatched_schedules
  python manage.py cleanup_grade_mismatched_schedules --verbose
"""
from django.core.management.base import BaseCommand

from schedules.assignment import clear_student_slot, get_student_level_types
from schedules.models import Schedule
from students.models import Student


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
    help = "Elimina asignaciones de horario que no correspondan al grado actual del estudiante."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra que cambios haria, sin escribir en la BD.',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Lista cada asignacion obsoleta encontrada.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run: no se guardaran cambios.'))

        removed = 0
        affected_students = set()

        student_qs = Student.objects.all().only('student_id', 'name', 'lastname', 'grade')
        for student in batched(student_qs):
            valid_types = get_student_level_types(student)
            stale = (
                Schedule.objects
                .filter(student=student)
                .exclude(block__type__in=valid_types)
                .select_related('block', 'block__workshop')
            )
            for sched in stale:
                removed += 1
                affected_students.add(student.student_id)
                if verbose:
                    self.stdout.write(
                        f"  - {student.name} {student.lastname} (grado {student.grade}): "
                        f"quitar {sched.block.workshop.name} "
                        f"[{sched.block.day} bloque {sched.block.block_number} tipo={sched.block.type}]"
                    )
                if not dry_run:
                    clear_student_slot(
                        student, sched.block.day, sched.block.block_number, sched.block.type
                    )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Resumen:'))
        self.stdout.write(f'  asignaciones obsoletas encontradas: {removed}')
        self.stdout.write(f'  estudiantes afectados: {len(affected_students)}')

        if dry_run:
            self.stdout.write(self.style.WARNING(
                'Ejecuta sin --dry-run para aplicar los cambios.'
            ))
