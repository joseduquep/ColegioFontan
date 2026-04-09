import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horariosfontanproyecto.settings')
django.setup()

from schedules.models import Schedule

res = []
for s in Schedule.objects.filter(student_id=280).order_by('block__day', 'block__block_number'):
    res.append({
        'day': s.block.day,
        'block': s.block.block_number,
        'block_type': getattr(s.block, 'type', 'none'),
        'ws_type': s.block.workshop.type,
        'ws_name': s.block.workshop.name
    })

print(json.dumps(res, indent=2, ensure_ascii=False))
