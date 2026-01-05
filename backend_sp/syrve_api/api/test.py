from goods.models import Group

for g in Group.objects.all():
    if g.parent_id == g.id:
        print("⚠️ Сам собі батько:", g.name)

    if g.parent and g.parent.parent_id == g.id:
        print("⚠️ Цикл між:", g.name, "<->", g.parent.name)
