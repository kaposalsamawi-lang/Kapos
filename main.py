# -*- coding: utf-8 -*-
import os
import csv
import sqlite3
import shutil
from datetime import date, datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

KV = r"""
#:import dp kivy.metrics.dp

<RTLLabel@Label>:
    halign: "right"
    valign: "middle"
    text_size: self.size

<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(12)
        RTLLabel:
            text: "نظام إدارة الكميات وقواعد البيانات"
            font_size: "23sp"
            bold: True
            size_hint_y: None
            height: dp(70)
        RTLLabel:
            text: "اسم المستخدم"
            size_hint_y: None
            height: dp(35)
        TextInput:
            id: username
            multiline: False
            size_hint_y: None
            height: dp(48)
            halign: "right"
        RTLLabel:
            text: "كلمة المرور"
            size_hint_y: None
            height: dp(35)
        TextInput:
            id: password
            password: True
            multiline: False
            size_hint_y: None
            height: dp(48)
            halign: "right"
        Button:
            text: "دخول"
            size_hint_y: None
            height: dp(52)
            on_release: root.login()
        RTLLabel:
            text: "الدخول الافتراضي: admin / 1234"
            size_hint_y: None
            height: dp(35)

<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        spacing: dp(5)
        padding: dp(5)
        BoxLayout:
            size_hint_y: None
            height: dp(52)
            Button:
                text: "الرئيسية"
                on_release: root.show_dashboard()
            Button:
                text: "العمليات"
                on_release: root.show_operations()
            Button:
                text: "البحث"
                on_release: root.show_search()
            Button:
                text: "الجهات"
                on_release: root.show_destinations()
        BoxLayout:
            size_hint_y: None
            height: dp(52)
            Button:
                text: "التقارير"
                on_release: root.show_reports()
            Button:
                text: "المستخدمون"
                on_release: root.show_users()
            Button:
                text: "تحديث"
                on_release: root.refresh_all()
            Button:
                text: "خروج"
                on_release: app.logout()
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: content
                cols: 1
                spacing: dp(8)
                padding: dp(8)
                size_hint_y: None
                height: self.minimum_height
"""

Builder.load_string(KV)

def db_path():
    return os.path.join(App.get_running_app().user_data_dir, "database.db")

def initialize_database():
    db = sqlite3.connect(db_path())
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS destinations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS operations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        quantity REAL,
        destination_id INTEGER,
        description TEXT,
        balance REAL,
        user_id INTEGER)""")
    if not c.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        c.execute("INSERT INTO users(username,password,role) VALUES('admin','1234','مدير')")
    db.commit()
    db.close()

class LoginScreen(Screen):
    def login(self):
        u = self.ids.username.text.strip()
        p = self.ids.password.text
        if not u or not p:
            popup("تنبيه", "أدخل اسم المستخدم وكلمة المرور")
            return
        try:
            initialize_database()
            db = sqlite3.connect(db_path())
            row = db.execute(
                "SELECT username, role FROM users WHERE username=? AND password=?",
                (u, p)).fetchone()
            db.close()
            if row:
                app = App.get_running_app()
                app.current_user = row[0]
                app.current_role = row[1]
                app.sm.current = "main"
                app.main_screen.show_dashboard()
            else:
                popup("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")
        except Exception as e:
            popup("خطأ", str(e))

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = None

    def on_pre_enter(self):
        self.open_db()

    def open_db(self):
        if self.conn is None:
            self.conn = sqlite3.connect(db_path())
            self.conn.execute("PRAGMA foreign_keys=ON")

    def on_leave(self):
        pass

    def clear(self):
        self.ids.content.clear_widgets()

    def label(self, text, size=18, bold=False):
        w = Label(text=text, font_size=f"{size}sp", bold=bold,
                  halign="right", valign="middle", size_hint_y=None,
                  height=45)
        w.bind(size=lambda x, v: setattr(x, "text_size", x.size))
        return w

    def button(self, text, callback):
        b = Button(text=text, size_hint_y=None, height=48)
        b.bind(on_release=callback)
        return b

    def card(self, title, value):
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=95,
                        padding=8, spacing=2)
        box.add_widget(self.label(title, 15, True))
        box.add_widget(self.label(value, 25, True))
        return box

    def rows(self, where="", params=()):
        q = """SELECT o.id,o.date,o.type,o.quantity,
                      COALESCE(d.name,''),o.description,o.balance
               FROM operations o
               LEFT JOIN destinations d ON d.id=o.destination_id"""
        if where:
            q += " WHERE " + where
        q += " ORDER BY o.date DESC,o.id DESC"
        return self.conn.execute(q, params).fetchall()

    def recalc(self):
        bal = 0
        rows = self.conn.execute(
            "SELECT id,type,quantity FROM operations ORDER BY date,id").fetchall()
        for oid, typ, q in rows:
            bal += q if typ == "وارد" else -q
            self.conn.execute("UPDATE operations SET balance=? WHERE id=?", (bal, oid))
        self.conn.commit()

    def show_dashboard(self):
        self.open_db()
        self.recalc()
        self.clear()
        inc = self.conn.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM operations WHERE type='وارد'").fetchone()[0]
        out = self.conn.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM operations WHERE type='مصروف'").fetchone()[0]
        bal = inc - out
        self.ids.content.add_widget(self.label("لوحة التحكم", 24, True))
        self.ids.content.add_widget(self.card("إجمالي الوارد", f"{inc:g}"))
        self.ids.content.add_widget(self.card("إجمالي المصروف", f"{out:g}"))
        self.ids.content.add_widget(self.card("الرصيد الحالي", f"{bal:g}"))
        self.ids.content.add_widget(self.label("آخر العمليات", 18, True))
        for r in self.rows()[:20]:
            self.ids.content.add_widget(self.label(
                f"#{r[0]} | {r[1]} | {r[2]} | {r[3]:g} | {r[4]} | {r[5]} | الرصيد {r[6]:g}", 13))

    def show_operations(self):
        self.open_db()
        self.clear()
        self.ids.content.add_widget(self.label("إضافة عملية", 22, True))
        date_in = TextInput(text=date.today().isoformat(), multiline=False, hint_text="YYYY-MM-DD",
                            size_hint_y=None, height=48, halign="right")
        qty_in = TextInput(multiline=False, hint_text="الكمية", input_filter="float",
                           size_hint_y=None, height=48, halign="right")
        desc_in = TextInput(multiline=False, hint_text="الوصف",
                            size_hint_y=None, height=48, halign="right")
        typ = Spinner(text="وارد", values=("وارد", "مصروف"), size_hint_y=None, height=48)
        dests = [""] + [r[0] for r in self.conn.execute(
            "SELECT name FROM destinations ORDER BY name").fetchall()]
        dest = Spinner(text="", values=dests, size_hint_y=None, height=48)

        for title, widget in [
            ("التاريخ", date_in), ("النوع", typ), ("الكمية", qty_in),
            ("الجهة", dest), ("الوصف", desc_in)
        ]:
            self.ids.content.add_widget(self.label(title, 14, True))
            self.ids.content.add_widget(widget)

        def add(_):
            try:
                datetime.strptime(date_in.text.strip(), "%Y-%m-%d")
                q = float(qty_in.text)
                if q <= 0:
                    raise ValueError
            except Exception:
                popup("خطأ", "أدخل تاريخًا صحيحًا YYYY-MM-DD وكمية موجبة")
                return
            did = None
            if dest.text.strip():
                rr = self.conn.execute(
                    "SELECT id FROM destinations WHERE name=?", (dest.text.strip(),)).fetchone()
                if not rr:
                    popup("خطأ", "الجهة غير موجودة")
                    return
                did = rr[0]
            uid = self.conn.execute(
                "SELECT id FROM users WHERE username=?",
                (App.get_running_app().current_user,)).fetchone()[0]
            self.conn.execute("""INSERT INTO operations
                (date,type,quantity,destination_id,description,user_id)
                VALUES(?,?,?,?,?,?)""",
                (date_in.text.strip(), typ.text, q, did, desc_in.text.strip(), uid))
            self.conn.commit()
            popup("تم", "تمت إضافة العملية")
            self.show_operations()

        self.ids.content.add_widget(self.button("إضافة العملية", add))
        self.ids.content.add_widget(self.label("العمليات", 18, True))
        for r in self.rows():
            line = BoxLayout(size_hint_y=None, height=55, spacing=4)
            line.add_widget(self.label(f"#{r[0]} {r[1]} {r[2]} {r[3]:g}", 12))
            b = Button(text="حذف", size_hint_x=None, width=80)
            def delete(_, oid=r[0]):
                self.conn.execute("DELETE FROM operations WHERE id=?", (oid,))
                self.conn.commit()
                self.show_operations()
            b.bind(on_release=delete)
            line.add_widget(b)
            self.ids.content.add_widget(line)

    def show_search(self):
        self.open_db()
        self.clear()
        self.ids.content.add_widget(self.label("البحث والاستعلام", 22, True))
        sfrom = TextInput(multiline=False, hint_text="من YYYY-MM-DD", size_hint_y=None, height=48, halign="right")
        sto = TextInput(multiline=False, hint_text="إلى YYYY-MM-DD", size_hint_y=None, height=48, halign="right")
        sdest = TextInput(multiline=False, hint_text="الجهة", size_hint_y=None, height=48, halign="right")
        sword = TextInput(multiline=False, hint_text="كلمة في الوصف/النوع", size_hint_y=None, height=48, halign="right")
        for x in (sfrom, sto, sdest, sword):
            self.ids.content.add_widget(x)
        result_box = GridLayout(cols=1, spacing=4, size_hint_y=None)
        result_box.bind(minimum_height=result_box.setter("height"))
        self.ids.content.add_widget(result_box)

        def run(_):
            result_box.clear_widgets()
            cond, params = [], []
            if sfrom.text.strip(): cond.append("o.date>=?"); params.append(sfrom.text.strip())
            if sto.text.strip(): cond.append("o.date<=?"); params.append(sto.text.strip())
            if sdest.text.strip(): cond.append("COALESCE(d.name,'') LIKE ?"); params.append("%"+sdest.text.strip()+"%")
            if sword.text.strip():
                x = "%"+sword.text.strip()+"%"
                cond.append("(o.description LIKE ? OR o.type LIKE ?)")
                params += [x, x]
            rr = self.rows(" AND ".join(cond), params) if cond else self.rows()
            for r in rr:
                result_box.add_widget(self.label(
                    f"#{r[0]} | {r[1]} | {r[2]} | {r[3]:g} | {r[4]} | {r[5]} | {r[6]:g}", 12))

        self.ids.content.add_widget(self.button("بحث", run))

    def show_destinations(self):
        self.open_db()
        self.clear()
        self.ids.content.add_widget(self.label("إدارة الجهات", 22, True))
        name = TextInput(multiline=False, hint_text="اسم الجهة", size_hint_y=None, height=48, halign="right")
        notes = TextInput(multiline=False, hint_text="ملاحظات", size_hint_y=None, height=48, halign="right")
        self.ids.content.add_widget(name)
        self.ids.content.add_widget(notes)

        def add(_):
            n = name.text.strip()
            if not n:
                popup("تنبيه", "أدخل اسم الجهة")
                return
            try:
                self.conn.execute("INSERT INTO destinations(name,notes) VALUES(?,?)",
                                  (n, notes.text.strip()))
                self.conn.commit()
                self.show_destinations()
            except sqlite3.IntegrityError:
                popup("خطأ", "الجهة موجودة مسبقًا")
        self.ids.content.add_widget(self.button("إضافة الجهة", add))
        for did, n, no in self.conn.execute(
            "SELECT id,name,notes FROM destinations ORDER BY name"):
            self.ids.content.add_widget(self.label(f"#{did} | {n} | {no}", 13))

    def show_reports(self):
        self.open_db()
        self.clear()
        self.ids.content.add_widget(self.label("التقارير والنسخ الاحتياطي", 22, True))
        self.ids.content.add_widget(self.label(
            "الملفات تُحفظ داخل مجلد التطبيق على الهاتف.", 13))
        self.ids.content.add_widget(self.button("تصدير CSV", lambda _: self.csv_report()))
        self.ids.content.add_widget(self.button("تقرير نصي TXT", lambda _: self.txt_report()))
        self.ids.content.add_widget(self.button("نسخة احتياطية DB", lambda _: self.backup()))

    def csv_report(self):
        path = os.path.join(App.get_running_app().user_data_dir, "تقرير_الكميات.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["الرقم","التاريخ","النوع","الكمية","الجهة","الوصف","الرصيد"])
            w.writerows(reversed(self.rows()))
        popup("تم", f"تم حفظ التقرير:\n{path}")

    def txt_report(self):
        inc = self.conn.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM operations WHERE type='وارد'").fetchone()[0]
        out = self.conn.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM operations WHERE type='مصروف'").fetchone()[0]
        path = os.path.join(App.get_running_app().user_data_dir, "تقرير_الكميات.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("تقرير نظام إدارة الكميات\n")
            f.write("=" * 50 + "\n")
            f.write(f"إجمالي الوارد: {inc:g}\nإجمالي المصروف: {out:g}\nالرصيد: {inc-out:g}\n\n")
            for r in reversed(self.rows()):
                f.write(" | ".join(map(str, r)) + "\n")
        popup("تم", f"تم حفظ التقرير:\n{path}")

    def backup(self):
        self.conn.commit()
        path = os.path.join(App.get_running_app().user_data_dir, "نسخة_احتياطية.db")
        shutil.copy2(db_path(), path)
        popup("تم", f"تم إنشاء النسخة الاحتياطية:\n{path}")

    def show_users(self):
        self.open_db()
        self.clear()
        self.ids.content.add_widget(self.label("المستخدمون", 22, True))
        u = TextInput(multiline=False, hint_text="اسم المستخدم", size_hint_y=None, height=48, halign="right")
        p = TextInput(multiline=False, hint_text="كلمة المرور", password=True, size_hint_y=None, height=48, halign="right")
        role = Spinner(text="مستخدم", values=("مستخدم","مدير"), size_hint_y=None, height=48)
        for x in (u, p, role):
            self.ids.content.add_widget(x)

        def add(_):
            if not u.text.strip() or not p.text:
                popup("تنبيه", "أدخل البيانات")
                return
            try:
                self.conn.execute(
                    "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (u.text.strip(), p.text, role.text))
                self.conn.commit()
                self.show_users()
            except sqlite3.IntegrityError:
                popup("خطأ", "المستخدم موجود")
        self.ids.content.add_widget(self.button("إضافة مستخدم", add))
        for uid, un, rr in self.conn.execute(
            "SELECT id,username,role FROM users ORDER BY username"):
            self.ids.content.add_widget(self.label(f"#{uid} | {un} | {rr}", 13))

    def refresh_all(self):
        self.show_dashboard()

class QuantityApp(App):
    current_user = ""
    current_role = ""
    sm = None
    main_screen = None

    def build(self):
        initialize_database()
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.main_screen = MainScreen(name="main")
        self.sm.add_widget(self.main_screen)
        self.sm.current = "login"
        return self.sm

    def logout(self):
        self.current_user = ""
        self.current_role = ""
        self.sm.current = "login"

def popup(title, message):
    box = BoxLayout(orientation="vertical", padding=12, spacing=10)
    box.add_widget(Label(text=message, halign="center"))
    b = Button(text="موافق", size_hint_y=None, height=48)
    box.add_widget(b)
    p = Popup(title=title, content=box, size_hint=(0.9, 0.4))
    b.bind(on_release=p.dismiss)
    p.open()

if __name__ == "__main__":
    QuantityApp().run()
