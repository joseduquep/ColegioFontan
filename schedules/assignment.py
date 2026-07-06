"""
Asignación de estudiantes a bloques: mantiene Schedule y Block.students sincronizados.
"""
from django.db import transaction

from schedules.models import Schedule
from workshops.models import Block


class AssignmentConflict(Exception):
    """El estudiante ya tiene un taller distinto en ese mismo horario."""

    def __init__(self, existing_schedule):
        self.existing_schedule = existing_schedule
        super().__init__()


def get_student_level_types(student):
    """
    Retorna los tipos de nivel académico habilitados para el estudiante.
    Regla especial: grado 5 es mixto (primary + high_school).
    """
    if student.grade <= 0:
        return ['preschool']
    if student.grade == 5:
        return ['primary', 'high_school']
    if student.grade > 5:
        return ['high_school']
    return ['primary']


def unassign_stale_blocks(student):
    """
    Elimina las asignaciones (Schedule + Block.students) del estudiante que ya
    no correspondan a su nivel académico actual (por ejemplo, tras un cambio
    de grado que lo mueve de primaria a bachillerato).
    """
    valid_types = get_student_level_types(student)
    stale = (
        Schedule.objects
        .filter(student=student)
        .exclude(block__type__in=valid_types)
        .select_related('block')
    )
    for sched in stale:
        clear_student_slot(student, sched.block.day, sched.block.block_number, sched.block.type)


def get_block_capacity(block):
    w = block.workshop
    if w.type == 'collective':
        if block.type == 'preschool' and w.max_capacity_aux_preschool:
            return w.max_capacity_aux_preschool
        if block.type == 'high_school' and w.max_capacity_aux:
            return w.max_capacity_aux
        return w.max_capacity
    return w.max_capacity


def get_slot_schedule(student, day, block_number, block_type):
    return (
        Schedule.objects
        .filter(
            student=student,
            block__day=day,
            block__block_number=block_number,
            block__type=block_type,
        )
        .select_related('block', 'block__workshop')
        .first()
    )


def clear_student_slot(student, day, block_number, block_type):
    """Quita al estudiante de Schedule y de todos los bloques M2M de ese slot."""
    old_blocks = Block.objects.filter(
        students=student,
        day=day,
        block_number=block_number,
        type=block_type,
    )
    for old_block in old_blocks:
        old_block.students.remove(student)

    Schedule.objects.filter(
        student=student,
        block__day=day,
        block__block_number=block_number,
        block__type=block_type,
    ).delete()


def is_student_assigned_to_block(student, block):
    in_schedule = Schedule.objects.filter(student=student, block=block).exists()
    in_m2m = block.students.filter(pk=student.pk).exists()
    return in_schedule and in_m2m


@transaction.atomic
def assign_student_to_block(student, block, replace=False):
    """
    Asigna al estudiante a un bloque limpiando antes cualquier asignación previa
    en el mismo día, número de bloque y tipo de nivel.

    Con replace=False lanza AssignmentConflict si ya existe Schedule apuntando
    a otro bloque; con replace=True reemplaza la asignación existente.
    """
    existing = get_slot_schedule(
        student, block.day, block.block_number, block.type
    )
    if existing and existing.block_id != block.block_id and not replace:
        raise AssignmentConflict(existing)

    if is_student_assigned_to_block(student, block):
        return

    clear_student_slot(student, block.day, block.block_number, block.type)
    Schedule.objects.create(student=student, block=block)
    block.students.add(student)


@transaction.atomic
def unassign_student_slot(student, day, block_number, block_type):
    """Elimina la asignación del estudiante en un slot (Schedule + M2M)."""
    clear_student_slot(student, day, block_number, block_type)
