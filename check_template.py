with open('schedules/templates/schedules/students_in_block.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
print("=== SYNTAX CHECK ===")
print(f"Bad syntax (=='neutral'): {content.count(\"=='neutral'\")}")
print(f"Good syntax (== 'neutral'): {content.count(\"== 'neutral'\")}")
print(f"Bad syntax (=='present'): {content.count(\"=='present'\")}")
print(f"Good syntax (== 'present'): {content.count(\"== 'present'\")}")
print(f"Bad syntax (=='absent'): {content.count(\"=='absent'\")}")
print(f"Good syntax (== 'absent'): {content.count(\"== 'absent'\")}")
