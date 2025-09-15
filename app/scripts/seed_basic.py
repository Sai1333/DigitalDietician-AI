# app/scripts/seed_basic.py
from app.db.database import SessionLocal
from app.db.models import Recipe

RECIPES = [
    ("Scrambled Eggs","egg, salt, butter",10,200,12,1,15),
    ("Egg Fried Rice","rice, egg, soy sauce, oil, spring onion",18,520,18,70,18),
    ("Tomato Sandwich","bread, tomato, butter, salt",5,260,7,35,10),
    ("Paneer Bhurji","paneer, onion, tomato, turmeric, salt, oil",12,360,24,8,24),
    ("Chickpea Salad","chickpeas, cucumber, tomato, lemon, olive oil, salt",8,340,14,40,12),
    ("Peanut Butter Toast","bread, peanut butter",3,310,12,28,18),
    ("Omelette","egg, onion, tomato, salt, oil",9,230,14,3,17),
    ("Masala Oats","oats, water, carrot, peas, salt",7,280,9,45,5),
    ("Curd Rice","rice, curd, salt, mustard seeds, curry leaves, oil",10,420,10,65,11),
    ("Poha","poha, onion, peanut, turmeric, salt, oil",10,360,8,54,10),
    ("Upma","rava, onion, carrot, peas, oil, salt",12,380,9,58,10),
    ("Grilled Cheese","bread, cheese, butter",8,420,16,32,26),
    ("Veg Maggi","maggi, water, peas, carrot",6,390,9,60,12),
    ("Aloo Paratha","wheat flour, potato, salt, oil",20,450,10,70,14),
    ("Chicken Stir Fry","chicken, bell pepper, soy sauce, oil, garlic",15,480,35,18,20),
    ("Tofu Stir Fry","tofu, bell pepper, soy sauce, oil, garlic",15,420,28,18,18),
    ("Dal Tadka","toor dal, onion, tomato, turmeric, ghee, salt",25,360,18,44,10),
    ("Veg Pulao","rice, peas, carrot, beans, oil, salt",22,480,9,85,10),
    ("Pancakes","flour, milk, egg, sugar, butter",14,520,12,68,20),
    ("Fruit Yogurt Bowl","curd, banana, apple, honey",4,300,10,52,5),
]

def upsert_recipe(db, title, ingredients, time_m, cal, p, c, f):
    exists = db.query(Recipe).filter(Recipe.title == title).first()
    if exists:
        return exists
    r = Recipe(
        title=title,
        description="Seeded recipe",
        ingredients=ingredients,
        instructions="Mix, cook, and serve.",
        calories=cal, protein=p, carbs=c, fat=f,
        time_minutes=time_m
    )
    db.add(r); db.commit(); db.refresh(r)
    return r

def main():
    db = SessionLocal()
    for row in RECIPES:
        upsert_recipe(db, *row)
    db.close()
    print(f"Seeded {len(RECIPES)} recipes.")

if __name__ == "__main__":
    main()
