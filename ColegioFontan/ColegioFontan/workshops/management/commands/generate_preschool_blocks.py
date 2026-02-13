# workshops/management/commands/generate_preschool_blocks.py

from django.core.management.base import BaseCommand
from workshops.models import Workshop, Block
import datetime

class Command(BaseCommand):
    help = "Genera los bloques de Preescolar (4 L-J, 3 V) para todos los talleres Colectivo existentes."

    def to_iso(self, hm: str) -> datetime.time:
        """Convierte 'H:MM' a objeto time con ceros delante si hace falta."""
        h, m = hm.split(':')
        return datetime.time(int(h), int(m))

    def handle(self, *args, **options):
        # Definición de franjas horarias para Preescolar
        schedules = {
            'preschool': {
                'Monday-Thursday': [
                    ("08:20","08:55"),
                    ("10:00","10:50"),
                    ("10:55","11:45"),
                    ("13:30","14:30"),
                ],
                'Friday': [
                    ("08:20","08:55"),
                    ("10:00","10:50"),
                    ("10:55","11:45"),
                ],
            }
        }

        created = 0
        skipped = 0

        # Iteramos únicamente talleres Colectivo
        for workshop in Workshop.objects.filter(type='collective'):
            self.stdout.write(f"📋 Taller Colectivo: {workshop.name}")
            cfg = schedules['preschool']

            for day_group, slots in cfg.items():
                days = (["Monday","Tuesday","Wednesday","Thursday"]
                        if day_group=="Monday-Thursday" else ["Friday"])
                for day in days:
                    for idx, (start, end) in enumerate(slots, start=1):
                        # Si ya existe ese bloque, lo saltamos
                        exists = Block.objects.filter(
                            workshop=workshop,
                            type='preschool',
                            day=day,
                            block_number=idx
                        ).exists()
                        if exists:
                            skipped += 1
                            continue

                        Block.objects.create(
                            workshop=workshop,
                            day=day,
                            start_time=self.to_iso(start),
                            end_time=self.to_iso(end),
                            block_number=idx,
                            type='preschool'
                        )
                        created += 1
                        self.stdout.write(f"  ✔ Bloque Preescolar {day} #{idx}")

        self.stdout.write(self.style.SUCCESS(
            f"Listo! {created} bloques creados, {skipped} ya existían."
        ))
