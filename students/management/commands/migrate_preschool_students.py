from django.core.management.base import BaseCommand
from students.models import Student

class Command(BaseCommand):
    help = "Migra estudiantes de preescolar existentes (grade=0) a las nuevas categorías PJ, J, T"

    def handle(self, *args, **options):
        # Buscar estudiantes con grade = 0 (el antiguo "Preescolar")
        preschool_students = Student.objects.filter(grade=0)
        
        if not preschool_students.exists():
            self.stdout.write(self.style.SUCCESS("No hay estudiantes de preescolar para migrar."))
            return

        self.stdout.write(f"Encontrados {preschool_students.count()} estudiantes de preescolar para migrar:")
        self.stdout.write("\nOpciones disponibles:")
        self.stdout.write("  -3 = PJ (Prejardín)")
        self.stdout.write("  -2 = J (Jardín)")
        self.stdout.write("  -1 = T (Transición)")
        self.stdout.write("\n" + "="*50)

        migrated_count = 0
        
        for student in preschool_students:
            self.stdout.write(f"\nEstudiante: {student.name} {student.lastname}")
            self.stdout.write(f"ID: {student.student_id} | Código: {student.id_number}")
            
            while True:
                try:
                    choice = input("Seleccionar nivel (-3=PJ, -2=J, -1=T, s=saltar): ").strip().lower()
                    
                    if choice == 's':
                        self.stdout.write("  ⏭ Saltado")
                        break
                    elif choice in ['-3', '-2', '-1']:
                        new_grade = int(choice)
                        student.grade = new_grade
                        student.save()
                        
                        level_names = {-3: 'PJ (Prejardín)', -2: 'J (Jardín)', -1: 'T (Transición)'}
                        self.stdout.write(f"  ✅ Migrado a {level_names[new_grade]}")
                        migrated_count += 1
                        break
                    else:
                        self.stdout.write("  ❌ Opción inválida. Use -3, -2, -1 o s")
                        
                except (ValueError, KeyboardInterrupt):
                    self.stdout.write("\n  ⚠ Operación cancelada")
                    return

        self.stdout.write(f"\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Migración completada: {migrated_count} estudiantes migrados."))
        
        remaining = Student.objects.filter(grade=0).count()
        if remaining > 0:
            self.stdout.write(self.style.WARNING(f"Quedan {remaining} estudiantes sin migrar con grade=0.")) 