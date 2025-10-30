import tkinter as tk
from tkinter import messagebox
import random, json, os

# ---------- Player Class ----------
class Player:
    def __init__(self, name):
        self.name = name
        self.age = 18
        self.day = 0
        self.money = 800
        self.hunger = 80
        self.mood = 80
        self.intelligence = random.randint(30, 50)
        self.charm = random.randint(30, 50)
        self.salary = 0
        self.job = "Unemployed"
        self.house = "Rental Room"
        self.rent = 50

    def daily_update(self):
        self.day += 1
        if self.day % 10 == 0:
            self.age += 1
        self.money += self.salary
        self.money -= self.rent
        self.hunger -= 10
        self.mood -= 5
        if self.house == "Apartment":
            self.mood += 3
        elif self.house == "Villa":
            self.mood += 8
            self.charm += 3
        self.limit_attributes()

    def apply_event(self, effect_dict):
        for k, v in effect_dict.items():
            if callable(v):
                v(self)
            else:
                if k == "house":
                    self.house = v
                    if v == "Apartment":
                        self.rent = 200
                    elif v == "Villa":
                        self.rent = 500
                    else:
                        self.rent = 50
                elif k == "job":
                    self.job = v
                elif k == "salary":
                    self.salary += v
                else:
                    setattr(self, k, getattr(self, k) + v)
        self.limit_attributes()

    def limit_attributes(self):
        for attr in ["hunger", "mood", "intelligence", "charm"]:
            setattr(self, attr, max(0, min(100, getattr(self, attr))))
        self.money = max(0, self.money)

    def check_dead(self):
        if self.money <= 0:
            return "💸 You went bankrupt!"
        elif self.hunger <= 0:
            return "🍞 You died of hunger!"
        elif self.mood <= 0:
            return "😞 You fell into depression!"
        return None

# ---------- Attribute Mapping ----------
ATTR_EN = {
    "money": "Money",
    "hunger": "Hunger",
    "mood": "Mood",
    "intelligence": "Intelligence",
    "charm": "Charm",
    "house": "House",
    "salary": "Salary",
    "job": "Job"
}

# ---------- Attribute Icons ----------
ATTR_ICON = {
    "money": "💰",
    "hunger": "🍞",
    "mood": "😊",
    "intelligence": "🧠",
    "charm": "💖",
    "house": "🏠",
    "salary": "💵",
    "job": "👔"
}

# ---------- Food ----------
FOODS = [
    {"name": "Bread", "price": 20, "hunger": 8, "mood": 2},
    {"name": "Fast Food", "price": 50, "hunger": 15, "mood": 5},
    {"name": "Deluxe Meal", "price": 100, "hunger": 25, "mood": 10},
]

# ---------- House Events ----------
HOUSE_EVENTS = [
    {"text": "An apartment is available for rent. Move in?",
     "condition": {"intelligence": 50},
     "choices": {"Move in": {"money": -1000, "house": "Apartment", "mood": +5}}},
    {"text": "A luxury villa is for sale. Do you want to buy it?",
     "condition": {"intelligence": 80, "charm": 70},
     "choices": {"Buy": {"money": -5000, "house": "Villa", "mood": +8, "charm": +5}}}
]

# ---------- Jobs ----------
JOBS = [
    {"name": "Part-time", "condition": {"intelligence": 0}, "salary": 30, "mood_effect": 0},
    {"name": "Office Worker", "condition": {"intelligence": 50}, "salary": 100, "mood_effect": +2},
    {"name": "Executive", "condition": {"intelligence": 80, "charm": 70}, "salary": 300, "mood_effect": +5},
]

# ---------- Random Events ----------
EVENTS = [
    {"text": "You see a stray cat. Feed it?",
     "choices": {
         "Feed it": {"money": -20, "charm": +2, "mood": +5},
         "Ignore it": {"money": 0, "charm": -2, "mood": -10}}},
    {"text": "A friend invites you to dinner. Go?",
     "choices": {
         "Go": {"money": -80, "mood": +10, "charm": +2},
         "Decline": {"money": 0, "mood": -15, "charm": -5}}},
    {"text": "You stay up late to study.",
     "choices": {
         "Study hard": {"intelligence": +5, "mood": -5},
         "Rest": {"intelligence": 0, "mood": -3}}},
    {"text": "Outdoor exercise improves mood but costs money.",
     "choices": {
         "Join": {"money": -100, "mood": +8, "hunger": -5},
         "Skip": {"money": 0, "mood": -12, "hunger": 0}}},
    {"text": "Someone asks for your help. Will you help?",
     "choices": {
         "Help": {"money": -50, "mood": +5, "charm": +3},
         "Ignore": {"money": 0, "mood": -8, "charm": -3}}},
    {"text": "Your company offers training. Join?",
     "condition": {"intelligence": 50},
     "choices": {
         "Join": {"intelligence": +5, "mood": -2, "salary": +20},
         "Skip": {"intelligence": 0, "mood": -10}}},
    {"text": "A friend invites you on a trip.",
     "choices": {
         "Go": {"money": -200, "mood": +15},
         "Skip": {"money": 0, "mood": -15}}},
    {"text": "You encounter a mental challenge (requires Intelligence ≥ 60).",
     "condition": {"intelligence": 60},
     "choices": {
         "Challenge": {"intelligence": +5, "mood": +3, "money": +50},
         "Give up": {"intelligence": 0, "mood": -10}}},
    {"text": "You're invited to a social event (Charm ≥ 70 gives extra rewards).",
     "condition": {"charm": 70},
     "choices": {
         "Join": {"mood": +8, "charm": +5, "money": -50},
         "Decline": {"mood": -15}}}
]

# ---------- Main App ----------
class LifeSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("9001_Life Simulator")
        self.root.geometry("750x650")
        self.player = None
        self.events_today = 0
        self.current_event = None
        self.recent_events = []
        self.max_recent = 6
        self.record_file = "record.json"
        if not os.path.exists(self.record_file):
            json.dump({"max_day": 0, "max_money": 0, "best_player": ""}, open(self.record_file, "w"))
        self.main_menu()

    # ---------- Main Menu ----------
    def main_menu(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text="🌟 Life Simulator 🌟", font=("Arial", 20, "bold")).pack(pady=40)
        tk.Button(self.root, text="Start Game", width=20, height=2, command=self.start_game).pack(pady=10)
        tk.Button(self.root, text="Leaderboard", width=20, height=2, command=self.show_ranking).pack(pady=10)
        tk.Button(self.root, text="Quit", width=20, height=2, command=self.root.quit).pack(pady=10)

    # ---------- Start Game ----------
    def start_game(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text="Enter your name:", font=("Arial", 14)).pack(pady=20)
        name_entry = tk.Entry(self.root, font=("Arial", 14))
        name_entry.pack(pady=10)

        def confirm_name():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter your name!")
                return
            self.player = Player(name)
            self.events_today = 0
            self.game_screen()

        tk.Button(self.root, text="Confirm", width=20, command=confirm_name).pack(pady=20)
        tk.Button(self.root, text="Back to Main Menu", width=20, command=self.main_menu).pack()

    # ---------- Game Screen ----------
    def game_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.info_label = tk.Label(self.root, font=("Arial", 12), justify="left")
        self.info_label.pack(pady=10)
        self.event_label = tk.Label(self.root, font=("Arial", 12), fg="blue", wraplength=700)
        self.event_label.pack(pady=20)
        self.choice_frame = tk.Frame(self.root)
        self.choice_frame.pack(pady=10)
        tk.Button(self.root, text="Exit to Main Menu", command=self.main_menu).pack(pady=10)
        self.update_info()
        self.next_event()

    # ---------- Display Next Event ----------
    def next_event(self):
        for w in self.choice_frame.winfo_children():
            w.destroy()
        available_events=[]
        house_rank = {"Rental Room":1,"Apartment":2,"Villa":3}

        # House events
        for e in HOUSE_EVENTS:
            target_house = None
            for v in e['choices'].values():
                if isinstance(v, dict) and "house" in v:
                    target_house = v["house"]
            if not target_house: continue
            if house_rank[target_house] <= house_rank[self.player.house]:
                continue
            cond=e.get("condition")
            if cond and not all(getattr(self.player,k)>=v for k,v in cond.items()):
                continue
            choices = e['choices'].copy()
            choices["Don't Move"] = {}
            e['choices'] = choices
            available_events.append(e)

        # Lower house random event
        if self.player.house != "Rental Room" and random.random()<0.2:
            lower_house = [h for h,r in house_rank.items() if r < house_rank[self.player.house]]
            if lower_house:
                chosen = random.choice(lower_house)
                low_event = {"text":f"Move to {chosen} to save money?",
                             "choices":{
                                 f"Move to {chosen}": {"house":chosen,"money":-100,"mood":-2},
                                 "Don't Move": {}
                             }}
                available_events.append(low_event)

        # Job events
        available_jobs=[]
        for job in JOBS:
            if job["name"] == self.player.job:
                continue
            cond=job.get("condition",{})
            if all(getattr(self.player,k)>=v for k,v in cond.items()):
                available_jobs.append(job)
        if available_jobs and random.random()<0.3:
            chosen_job = random.choice(available_jobs)
            work_event = {"text":f"Company offers position: {chosen_job['name']}, accept?",
                          "choices":{
                              "Accept": {"salary":chosen_job["salary"] - self.player.salary,
                                         "mood":chosen_job["mood_effect"],
                                         "job":chosen_job["name"]},
                              "Decline": {}
                          }}
            available_events.append(work_event)

        # Filter random events
        filtered_events=[]
        for e in EVENTS:
            cond=e.get("condition")
            if cond and not all(getattr(self.player,k)>=v for k,v in cond.items()):
                continue
            if e["text"] in self.recent_events:
                continue
            filtered_events.append(e)

        if filtered_events and random.random()<0.7:
            self.current_event = random.choice(filtered_events)
        else:
            candidates = [e for e in EVENTS if e["text"] not in self.recent_events]
            self.current_event = random.choice(candidates) if candidates else random.choice(EVENTS)

        self.recent_events.append(self.current_event["text"])
        if len(self.recent_events) > self.max_recent:
            self.recent_events.pop(0)

        text=self.current_event['text']
        self.event_label.config(text=f"📢 Today's Event: {text}")
        for choice_text,effect in self.current_event['choices'].items():
            effect_str=[]
            for k,v in effect.items():
                name=ATTR_EN.get(k,k)
                icon=ATTR_ICON.get(k,"")
                if callable(v):
                    val="Depends on attribute"
                else:
                    if isinstance(v,int):
                        val=f"{'+' if v>=0 else ''}{v}"
                    else:
                        val=str(v)
                effect_str.append(f"{icon}{name} {val}")
            display_text=f"{choice_text} ({', '.join(effect_str)})"
            btn=tk.Button(self.choice_frame,text=display_text,width=60,command=lambda eff=effect:self.choose_event(eff))
            btn.pack(pady=5)

    # ---------- Player Choice ----------
    def choose_event(self,effect):
        self.player.apply_event(effect)
        self.events_today+=1
        death_msg=self.player.check_dead()
        if death_msg:
            messagebox.showinfo("Game Over",f"{death_msg}\nDays Survived:{self.player.day}")
            self.update_record()
            self.main_menu()
            return
        if self.events_today>=3:
            self.events_today=0
            self.food_screen()
        else:
            self.update_info()
            self.next_event()

    # ---------- Food Screen ----------
    def food_screen(self):
        for w in self.choice_frame.winfo_children():
            w.destroy()
        self.event_label.config(text="🍽️ Meal time! Choose your food")
        for food in FOODS:
            desc=f"{food['name']} (Price:{food['price']}, 🍞+{food['hunger']}, 😊+{food['mood']})"
            tk.Button(self.choice_frame,text=desc,width=60,
                      command=lambda f=food:self.eat_food(f)).pack(pady=5)

    def eat_food(self,food):
        if self.player.money<food['price']:
            messagebox.showwarning("Warning","Not enough money!")
            return
        self.player.money -= food['price']
        self.player.hunger += food['hunger']
        self.player.mood += food['mood']
        self.player.limit_attributes()
        self.player.daily_update()
        self.update_info()
        self.next_event()

    # ---------- Update Info ----------
    def update_info(self):
        info=f"""
👤 Name: {self.player.name}
🎂 Age: {self.player.age}
📅 Days Survived: {self.player.day}
💰 Money: {self.player.money}                  💵 Salary: {self.player.salary}   👔 Job: {self.player.job}
🍞 Hunger: {self.player.hunger}                   😊 Mood: {self.player.mood}
🧠 Intelligence: {self.player.intelligence}            💖 Charm: {self.player.charm}
🏠 House: {self.player.house}  Daily Rent: {self.player.rent}
"""
        self.info_label.config(text=info)

    # ---------- Leaderboard ----------
    def show_ranking(self):
        for w in self.root.winfo_children():
            w.destroy()
        with open(self.record_file,"r") as f:
            record=json.load(f)
        text=f"""
🏆 Leaderboard 🏆

Wealthiest Player: {record.get('best_player','')}
Max Wealth: {record.get('max_money',0)}
Longest Survival: {record.get('max_day',0)} days
"""
        tk.Label(self.root,text=text,font=("Arial",14),justify="left").pack(pady=30)
        tk.Button(self.root,text="Back to Main Menu",command=self.main_menu).pack(pady=20)

    # ---------- Update Record ----------
    def update_record(self):
        with open(self.record_file,"r") as f:
            record=json.load(f)
        if self.player.day > record.get("max_day",0):
            record["max_day"]=self.player.day
        if self.player.money > record.get("max_money",0):
            record["max_money"]=self.player.money
            record["best_player"]=self.player.name
        with open(self.record_file,"w") as f:
            json.dump(record,f)

# ---------- Run ----------
root=tk.Tk()
app=LifeSimulatorApp(root)
root.mainloop()
