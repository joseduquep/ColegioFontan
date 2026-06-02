from django.test import TestCase

from schedules.assignment import (
    AssignmentConflict,
    assign_student_to_block,
    is_student_assigned_to_block,
    unassign_student_slot,
)
from schedules.models import Schedule
from students.models import Student
from tutors.models import Tutor
from workshops.models import Block, Workshop
from django.contrib.auth.models import User


class AssignmentSyncTests(TestCase):
    def setUp(self):
        user = User.objects.create_user('tutor1', password='x')
        self.tutor = Tutor.objects.create(user=user)
        self.workshop_a = Workshop.objects.create(
            name='Taller A', tutor=self.tutor, type='primary'
        )
        self.workshop_b = Workshop.objects.create(
            name='Taller B', tutor=self.tutor, type='primary'
        )
        self.block_a = Block.objects.create(
            day='Monday',
            start_time='08:00',
            end_time='09:00',
            block_number=1,
            type='primary',
            workshop=self.workshop_a,
        )
        self.block_b = Block.objects.create(
            day='Monday',
            start_time='08:00',
            end_time='09:00',
            block_number=1,
            type='primary',
            workshop=self.workshop_b,
        )
        self.student = Student.objects.create(
            name='Ana',
            lastname='Test',
            id_number=12345,
            grade=3,
        )

    def test_assign_keeps_schedule_and_m2m_in_sync(self):
        assign_student_to_block(self.student, self.block_a)
        self.assertTrue(is_student_assigned_to_block(self.student, self.block_a))

    def test_assign_clears_orphan_m2m_on_same_slot(self):
        self.block_a.students.add(self.student)
        self.assertFalse(
            Schedule.objects.filter(student=self.student).exists()
        )
        assign_student_to_block(self.student, self.block_b)
        self.assertFalse(self.block_a.students.filter(pk=self.student.pk).exists())
        self.assertTrue(is_student_assigned_to_block(self.student, self.block_b))

    def test_assign_raises_conflict_when_schedule_on_other_block(self):
        Schedule.objects.create(student=self.student, block=self.block_a)
        self.block_a.students.add(self.student)
        with self.assertRaises(AssignmentConflict):
            assign_student_to_block(self.student, self.block_b)

    def test_unassign_clears_all_blocks_in_slot(self):
        self.block_a.students.add(self.student)
        self.block_b.students.add(self.student)
        Schedule.objects.create(student=self.student, block=self.block_a)
        unassign_student_slot(self.student, 'Monday', 1, 'primary')
        self.assertEqual(Schedule.objects.filter(student=self.student).count(), 0)
        self.assertFalse(Block.objects.filter(students=self.student).exists())
