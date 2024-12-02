from django.shortcuts import render
from workshops.models import Workshop

def create_workshops():

    workshops_created = []
    
    for letter in range(ord('A'), ord('Z') + 1):
        name = f"Taller {chr(letter)}"
        # Crea el taller si no existe
        workshop, created = Workshop.objects.get_or_create(name=name)
        if created:
            workshops_created.append(name)
    
    if workshops_created:
        print(f"Talleres creados: {', '.join(workshops_created)}")
    else:
        print("No se crearon talleres nuevos, ya existían todos.")

create_workshops()


