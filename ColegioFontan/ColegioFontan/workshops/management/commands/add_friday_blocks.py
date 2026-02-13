from django.core.management.base import BaseCommand
from workshops.models import Workshop, Block
import datetime

class Command(BaseCommand):
    help = "Agrega los bloques faltantes de viernes a todos los talleres existentes"

    def to_iso(self, hm: str) -> datetime.time:
        """Convierte 'H:MM' a objeto time."""
        h, m = hm.split(':')
        return datetime.time(int(h), int(m))

    def handle(self, *args, **options):
        # Horarios adicionales de viernes que faltan
        friday_schedules = {
            'preschool': {
                'new_block': ("13:30", "14:30")  # Bloque 4
            },
            'primary': {
                'new_block': ("13:50", "14:40")  # Bloque 5
            },
            'high_school': {
                'new_block': ("13:20", "14:40")  # Bloque 4
            }
        }

        created = 0
        skipped = 0

        # Procesar todos los talleres
        for workshop in Workshop.objects.all():
            self.stdout.write(f"📋 Procesando taller: {workshop.name} (tipo: {workshop.type})")
            
            if workshop.type == 'collective':
                # Para talleres colectivos, agregar bloques en los 3 niveles
                for level in ['preschool', 'primary', 'high_school']:
                    created_count, skipped_count = self.add_friday_block(workshop, level, friday_schedules[level])
                    created += created_count
                    skipped += skipped_count
            else:
                # Para talleres específicos, agregar solo su tipo
                level = workshop.type
                if level in friday_schedules:
                    created_count, skipped_count = self.add_friday_block(workshop, level, friday_schedules[level])
                    created += created_count
                    skipped += skipped_count

        self.stdout.write(self.style.SUCCESS(
            f"¡Proceso completado! {created} bloques creados, {skipped} ya existían."
        ))

    def add_friday_block(self, workshop, block_type, schedule):
        """Agregar el bloque faltante de viernes para un taller y tipo específico"""
        created = 0
        skipped = 0
        
        start_time, end_time = schedule['new_block']
        
        # Determinar el número de bloque según el tipo
        block_numbers = {
            'preschool': 4,
            'primary': 5,
            'high_school': 4
        }
        block_number = block_numbers[block_type]
        
        # Verificar si ya existe
        exists = Block.objects.filter(
            workshop=workshop,
            type=block_type,
            day='Friday',
            block_number=block_number
        ).exists()
        
        if exists:
            self.stdout.write(f"  ⚠ Ya existe bloque {block_type} Friday #{block_number}")
            skipped += 1
        else:
            Block.objects.create(
                workshop=workshop,
                day='Friday',
                start_time=self.to_iso(start_time),
                end_time=self.to_iso(end_time),
                block_number=block_number,
                type=block_type
            )
            self.stdout.write(f"  ✔ Creado bloque {block_type} Friday #{block_number} ({start_time}-{end_time})")
            created += 1
            
        return created, skipped 