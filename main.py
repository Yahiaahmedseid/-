import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import json
import pytz
import sys
import os

class AlgeriaPrayerTimesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تطبيق مواقيت الصلاة في الجزائر 🇩🇿")
        self.root.geometry("550x800")
        self.root.resizable(True, True)
        
        # تنسيق الألوان
        self.bg_color = "#f0f8ff"
        self.fg_color = "#2c3e50"
        self.accent_color = "#3498db"
        self.prayer_color = "#2980b9"
        self.algeria_green = "#006633"
        self.algeria_red = "#d21034"
        self.algeria_white = "#FFFFFF"
        
        self.root.configure(bg=self.bg_color)
        
        # إعداد المتغيرات
        self.wilayas = self.load_wilayas()
        self.cities = self.load_cities()
        self.current_timings = {}
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
        # تعيين قيمة افتراضية للولاية (الجزائر العاصمة)
        self.wilaya_combo.set("الجزائر")
        self.on_wilaya_selected()
        
    def load_wilayas(self):
        """تحميل قائمة ولايات الجزائر"""
        wilayas = [
            "الجزائر", "وهران", "قسنطينة", "عنابة", "باتنة", "بجاية", "بسكرة", "بشار",
            "البليدة", "البويرة", "تمنراست", "تبسة", "تلمسان", "تيارت", "تيزي وزو",
            "الجزائر الجديدة", "الجلفة", "جيجل", "سطيف", "سعيدة", "سكيكدة", "سيدي بلعباس",
            "قالمة", "المدية", "مستغانم", "المسيلة", "معسكر", "ورقلة", "أم البواقي", 
            "البيض", "إليزي", "برج بوعريريج", "بومرداس", "الطارف", "تندوف", "تيسمسيلت",
            "الوادي", "خنشلة", "سوق أهراس", "تيبازة", "ميلة", "عين الدفلى", "النعامة",
            "عين تيموشنت", "غرداية", "غليزان", "الطارف"
        ]
        return sorted(set(wilayas))  # إزالة التكرارات
    
    def load_cities(self):
        """تحميل المدن لكل ولاية"""
        cities_by_wilaya = {
            "الجزائر": ["الجزائر", "الجزائر الوسطى", "القبة", "باب الوادي", "الحراش", "بولوغين"],
            "وهران": ["وهران", "السانية", "بطيوة", "عين الترك", "مرسى الحجاج"],
            "قسنطينة": ["قسنطينة", "عين أعبيد", "الخروب", "زيغود يوسف", "حامة بوزيان"],
            "عنابة": ["عنابة", "سرايدي", "الحجار", "برحال", "عين الباردة"],
            "باتنة": ["باتنة", "فسديس", "عين جاسر", "تازولت", "إشمول"],
            "بجاية": ["بجاية", "أوقاس", "تازمالت", "سيدي عيش", "أمالو"],
            "بسكرة": ["بسكرة", "زريبة الوادي", "القنطرة", "أورلال", "مشونش"],
            "بشار": ["بشار", "لحمر", "بني ونيف", "القنادسة", "تبلبالة"],
            "البليدة": ["البليدة", "بوفاريك", "بوعينان", "الأربعاء", "الشبلي"],
            "البويرة": ["البويرة", "الأخضرية", "سور الغزلان", "بئر غبالو", "حيزر"],
            "تمنراست": ["تمنراست", "عين قزام", "عين أمقل", "إدلس", "تاظروك"],
            "تبسة": ["تبسة", "العوينات", "الشريعة", "العقلة", "بئر العاتر"],
            "تلمسان": ["تلمسان", "الرمشي", "صبرة", "غزوات", "حمام بوحجر"],
            "تيارت": ["تيارت", "مدروة", "عين دزاريت", "عين كرمس", "وادي ليلي"],
            "تيزي وزو": ["تيزي وزو", "عزازقة", "أزفون", "ذراع الميزان", "مشطرا"],
            "سطيف": ["سطيف", "عين أرنات", "عين أزال", "بوقاعة", "صالح باي"],
            "سكيكدة": ["سكيكدة", "عزابة", "القل", "الحروش", "الزيتونة"],
            "سيدي بلعباس": ["سيدي بلعباس", "تلاغ", "سيدي علي بوسيدي", "مرين", "رأس الماء"],
            "المدية": ["المدية", "الشهبونية", "العزيزية", "تابنة", "وزرة"],
            "مستغانم": ["مستغانم", "حاسي مماش", "عين تادلس", "خير الدين", "سيدي علي"],
            "المسيلة": ["المسيلة", "بوسعادة", "أولاد سليمان", "سيدي عيسى", "المعاضيد"],
            "معسكر": ["معسكر", "سيق", "غريس", "زهانة", "ماوسة"],
            "ورقلة": ["ورقلة", "حاسي مسعود", "البرمة", "انقوسة", "حاسي بن عبد الله"],
            "أم البواقي": ["أم البواقي", "عين بابوش", "سوق نعمان", "عين البيضاء", "فكيرينة"],
            "البيض": ["البيض", "بوقطب", "الغاسول", "البنود", "بريزينة"],
            "إليزي": ["إليزي", "جانت", "برج عمر إدريس", "عين امناس", "دبداب"],
            "برج بوعريريج": ["برج بوعريريج", "رأس الوادي", "الحمادية", "بئر قصد علي", "برج زمورة"],
            "بومرداس": ["بومرداس", "الثنية", "دلس", "بغلية", "يسر"],
            "الطارف": ["الطارف", "بن مهيدي", "بوحجار", "الطارف المركز", "العيون"],
            "تندوف": ["تندوف", "أم العسل", "تبلبالة تندوف"],
            "تيسمسيلت": ["تيسمسيلت", "ثنية الحد", "خميستي", "لرجام", "عماري"],
            "الوادي": ["الوادي", "البياضة", "قمار", "الرباح", "الطريفاوي"],
            "خنشلة": ["خنشلة", "قايس", "الشحنة", "عين الطويلة", "يابوس"],
            "سوق أهراس": ["سوق أهراس", "سدراتة", "الحدادة", "الراقوبة", "الزعرورية"],
            "تيبازة": ["تيبازة", "شرشال", "فوكة", "حجوط"],
            "ميلة": ["ميلة", "فرجيوة", "شلغوم العيد", "تسالة لمطاعي", "عين الملوك"],
            "عين الدفلى": ["عين الدفلى", "خميس مليانة", "بوراشد", "جندل", "العسافرة"],
            "النعامة": ["النعامة", "مغرار", "عين الصفراء", "عسلة", "مكمن بن عمار"],
            "عين تيموشنت": ["عين تيموشنت", "بني صاف", "حمام بوحجر", "العامرية", "أولاد الكيحل"],
            "غرداية": ["غرداية", "متليلي", "زلفانة", "بونورة", "ضاية بن ضحوة"],
            "غليزان": ["غليزان", "وادي رهيو", "الحمادنة", "عمي موسى", "بني زنطيس"]
        }
        
        # التأكد من أن جميع الولايات موجودة في القاموس
        for wilaya in self.wilayas:
            if wilaya not in cities_by_wilaya:
                cities_by_wilaya[wilaya] = [wilaya]
        
        return cities_by_wilaya
    
    def create_widgets(self):
        # العنوان الرئيسي مع العلم الجزائري
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=10)
        
        # علم الجزائر
        flag_frame = tk.Frame(title_frame, bg=self.bg_color)
        flag_frame.pack()
        
        tk.Frame(flag_frame, bg=self.algeria_green, width=150, height=30).pack(side=tk.LEFT, padx=2)
        tk.Frame(flag_frame, bg=self.algeria_white, width=150, height=30).pack(side=tk.LEFT, padx=2)
        tk.Frame(flag_frame, bg=self.algeria_red, width=150, height=30).pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            title_frame, 
            text="🇩🇿 تطبيق مواقيت الصلاة في الجزائر", 
            font=("Arial", 22, "bold"),
            bg=self.bg_color,
            fg=self.algeria_green
        ).pack(pady=10)
        
        # إطار اختيار الموقع
        location_frame = tk.LabelFrame(self.root, text="اختر موقعك", font=("Arial", 12, "bold"),
                                       bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        location_frame.pack(pady=15, padx=20, fill=tk.X)
        
        # اختيار الولاية
        tk.Label(
            location_frame, 
            text="الولاية:", 
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.wilaya_combo = ttk.Combobox(
            location_frame, 
            values=self.wilayas,
            state="readonly",
            font=("Arial", 11),
            width=30
        )
        self.wilaya_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # اختيار المدينة
        tk.Label(
            location_frame, 
            text="المدينة:", 
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.city_combo = ttk.Combobox(
            location_frame, 
            state="readonly",
            font=("Arial", 11),
            width=30
        )
        self.city_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # ربط الأحداث
        self.wilaya_combo.bind("<<ComboboxSelected>>", self.on_wilaya_selected)
        
        # زر الحصول على مواقيت الصلاة
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.get_times_btn = tk.Button(
            button_frame,
            text="🕌 احصل على مواقيت الصلاة",
            font=("Arial", 14, "bold"),
            bg=self.algeria_green,
            fg="white",
            command=self.get_prayer_times,
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.get_times_btn.pack()
        
        # إطار المعلومات
        info_frame = tk.LabelFrame(self.root, text="معلومات اليوم", font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # توزيع معلومات اليوم في إطارين داخليين
        date_frame = tk.Frame(info_frame, bg=self.bg_color)
        date_frame.pack(fill=tk.X, pady=5)
        
        time_frame = tk.Frame(info_frame, bg=self.bg_color)
        time_frame.pack(fill=tk.X, pady=5)
        
        # التاريخ
        self.gregorian_label = tk.Label(
            date_frame,
            text="التاريخ الميلادي: --/--/----",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.gregorian_label.pack(side=tk.LEFT, padx=10)
        
        self.hijri_label = tk.Label(
            date_frame,
            text="التاريخ الهجري: --/--/----",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.algeria_red
        )
        self.hijri_label.pack(side=tk.RIGHT, padx=10)
        
        # الوقت الحالي
        self.current_time_label = tk.Label(
            time_frame,
            text="الوقت الحالي: --:--:--",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.algeria_green
        )
        self.current_time_label.pack()
        
        # إطار مواقيت الصلاة
        prayer_frame = tk.LabelFrame(self.root, text="مواقيت الصلاة", font=("Arial", 14, "bold"),
                                     bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        prayer_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        # تسميات مواقيت الصلاة
        prayers = ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"]
        self.prayer_labels = {}
        self.time_labels = {}
        
        for i, prayer in enumerate(prayers):
            # إطار لكل صلاة
            prayer_item_frame = tk.Frame(prayer_frame, bg=self.bg_color)
            prayer_item_frame.pack(fill=tk.X, pady=8, padx=10)
            
            # رمز الصلاة
            icons = ["🌅", "☀️", "🕛", "🕒", "🌇", "🌙"]
            icon_label = tk.Label(
                prayer_item_frame,
                text=icons[i],
                font=("Arial", 16),
                bg=self.bg_color
            )
            icon_label.pack(side=tk.LEFT, padx=5)
            
            # اسم الصلاة
            self.prayer_labels[prayer] = tk.Label(
                prayer_item_frame,
                text=prayer,
                font=("Arial", 14, "bold"),
                bg=self.bg_color,
                fg=self.prayer_color,
                width=10,
                anchor=tk.W
            )
            self.prayer_labels[prayer].pack(side=tk.LEFT, padx=10)
            
            # وقت الصلاة
            self.time_labels[prayer] = tk.Label(
                prayer_item_frame,
                text="--:--",
                font=("Arial", 14, "bold"),
                bg=self.bg_color,
                fg=self.fg_color,
                width=8
            )
            self.time_labels[prayer].pack(side=tk.RIGHT, padx=10)
            
            # خط فاصل
            if i < len(prayers) - 1:
                separator = tk.Frame(prayer_frame, height=1, bg="#e0e0e0")
                separator.pack(fill=tk.X, padx=20, pady=2)
        
        # إطار الصلاة التالية
        next_prayer_frame = tk.Frame(prayer_frame, bg=self.bg_color)
        next_prayer_frame.pack(pady=15, fill=tk.X, padx=20)
        
        self.next_prayer_label = tk.Label(
            next_prayer_frame,
            text="الصلاة التالية: --",
            font=("Arial", 12),
            bg=self.algeria_green,
            fg="white",
            padx=15,
            pady=8,
            relief=tk.RAISED
        )
        self.next_prayer_label.pack()
        
        # معلومات التطبيق في الأسفل
        footer_frame = tk.Frame(self.root, bg=self.bg_color)
        footer_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(
            footer_frame,
            text="تطبيق مواقيت الصلاة للولايات الجزائرية\nAPI: Aladhan.com",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="gray"
        ).pack()
        
        # بدء تحديث الوقت
        self.update_current_time()
    
    def on_wilaya_selected(self, event=None):
        """عند اختيار ولاية"""
        selected_wilaya = self.wilaya_combo.get()
        if selected_wilaya in self.cities:
            cities_list = self.cities[selected_wilaya]
            self.city_combo['values'] = cities_list
            if cities_list:
                self.city_combo.set(cities_list[0])
    
    def update_current_time(self):
        """تحديث الوقت الحالي"""
        try:
            # الحصول على الوقت الحالي
            now = datetime.now()
            gregorian_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            
            self.gregorian_label.config(text=f"التاريخ الميلادي: {gregorian_date}")
            self.current_time_label.config(text=f"الوقت الحالي: {current_time}")
            
            # تحديث التاريخ الهجري كل دقيقة
            if now.second == 0:
                hijri_date = self.get_hijri_date()
                self.hijri_label.config(text=f"التاريخ الهجري: {hijri_date}")
            
            # تحديث الصلاة التالية
            self.update_next_prayer()
            
        except Exception as e:
            print(f"Error updating time: {e}")
        
        # تحديث كل ثانية
        self.root.after(1000, self.update_current_time)
    
    def get_hijri_date(self):
        """الحصول على التاريخ الهجري"""
        try:
            # استخدام API للحصول على التاريخ الهجري
            today = datetime.now().strftime("%d-%m-%Y")
            response = requests.get(f"http://api.aladhan.com/v1/gToH?date={today}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                hijri_date = data['data']['hijri']['date']
                return hijri_date
        except:
            pass
        return "---"
    
    def update_next_prayer(self):
        """تحديث الصلاة التالية"""
        if not self.current_timings:
            return
        
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_hour, current_minute = map(int, current_time.split(":"))
            current_total_minutes = current_hour * 60 + current_minute
            
            prayers_order = ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"]
            next_prayer = None
            min_time_diff = 24 * 60  # عدد الدقائق في اليوم
            
            for prayer in prayers_order:
                if prayer in self.time_labels:
                    prayer_time_str = self.time_labels[prayer].cget("text")
                    if prayer_time_str != "--:--":
                        prayer_hour, prayer_minute = map(int, prayer_time_str.split(":"))
                        prayer_total_minutes = prayer_hour * 60 + prayer_minute
                        
                        # حساب الفرق الزمني
                        time_diff = prayer_total_minutes - current_total_minutes
                        
                        # إذا مر الوقت اليوم، نضيف 24 ساعة
                        if time_diff < 0:
                            time_diff += 24 * 60
                        
                        # إذا كان هذا الفرق هو الأقل وكان موجباً
                        if 0 < time_diff < min_time_diff:
                            min_time_diff = time_diff
                            next_prayer = prayer
            
            if next_prayer:
                hours = min_time_diff // 60
                minutes = min_time_diff % 60
                time_str = f"بعد {hours} ساعة و {minutes} دقيقة" if hours > 0 else f"بعد {minutes} دقيقة"
                self.next_prayer_label.config(text=f"الصلاة التالية: {next_prayer} ({time_str})")
            else:
                self.next_prayer_label.config(text="الصلاة التالية: --")
                
        except Exception as e:
            print(f"Error updating next prayer: {e}")
    
    def get_prayer_times(self):
        """الحصول على مواقيت الصلاة من API"""
        wilaya = self.wilaya_combo.get()
        city = self.city_combo.get()
        
        if not wilaya or not city:
            messagebox.showwarning("تحذير", "الرجاء اختيار الولاية والمدينة")
            return
        
        try:
            # تغيير نص الزر أثناء التحميل
            self.get_times_btn.config(text="⏳ جاري التحميل...", state=tk.DISABLED)
            self.root.update()
            
            # استخدام API Aladhan.com
            today = datetime.now().strftime("%d-%m-%Y")
            
            # البحث باستخدام اسم المدينة
            response = requests.get(
                f"http://api.aladhan.com/v1/timingsByCity/{today}",
                params={
                    "city": city,
                    "country": "Algeria",
                    "method": 2  # طريقة جامعة الأزهر
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'timings' in data['data']:
                    timings = data['data']['timings']
                    
                    # تحديث أوقات الصلاة
                    prayer_times = {
                        "الفجر": timings.get('Fajr', '--:--'),
                        "الشروق": timings.get('Sunrise', '--:--'),
                        "الظهر": timings.get('Dhuhr', '--:--'),
                        "العصر": timings.get('Asr', '--:--'),
                        "المغرب": timings.get('Maghrib', '--:--'),
                        "العشاء": timings.get('Isha', '--:--')
                    }
                    
                    self.current_timings = prayer_times
                    
                    for prayer, time in prayer_times.items():
                        self.time_labels[prayer].config(text=time)
                    
                    # تحديث التاريخ الهجري
                    if 'date' in data['data'] and 'hijri' in data['data']['date']:
                        hijri_date = data['data']['date']['hijri']['date']
                        self.hijri_label.config(text=f"التاريخ الهجري: {hijri_date}")
                    
                    # تحديث العنوان
                    self.root.title(f"🇩🇿 مواقيت الصلاة في {city}, {wilaya}")
                    
                    messagebox.showinfo("نجاح", f"تم تحميل مواقيت الصلاة لـ {city}, {wilaya}")
                    
                else:
                    messagebox.showerror("خطأ", "تعذر الحصول على مواقيت الصلاة. تأكد من اتصال الإنترنت.")
            else:
                messagebox.showerror("خطأ", f"خطأ في الاتصال بالخادم: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("خطأ", f"تعذر الاتصال بالإنترنت: {str(e)}")
            
            # عرض أوقات افتراضية (لأغراض الاختبار)
            default_times = {
                "الفجر": "05:30",
                "الشروق": "07:00",
                "الظهر": "12:45",
                "العصر": "16:00",
                "المغرب": "18:30",
                "العشاء": "20:00"
            }
            
            self.current_timings = default_times
            
            for prayer, time in default_times.items():
                self.time_labels[prayer].config(text=time)
            
            messagebox.showinfo("ملاحظة", "تم عرض أوقات افتراضية. تحقق من اتصالك بالإنترنت للحصول على الأوقات الدقيقة.")
        
        finally:
            # إعادة نص الزر إلى وضعه الطبيعي
            self.get_times_btn.config(text="🕌 احصل على مواقيت الصلاة", state=tk.NORMAL)

def main():
    root = tk.Tk()
    
    # إضافة أيقونة للتطبيق (إذا وجدت)
    try:
        root.iconbitmap("icon.ico")  # يمكنك إضافة أيقونة في نفس المجلد
    except:
        pass
    
    app = AlgeriaPrayerTimesApp(root)
    
    # جعل النوافذ قابلة للتكبير والتصغير بشكل مناسب
    root.update_idletasks()
    
    # تشغيل التطبيق
    root.mainloop()

if __name__ == "__main__":
    main()
