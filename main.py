import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import json
import pytz

class AlgeriaPrayerTimesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تطبيق مواقيت الصلاة في الجزائر")
        self.root.geometry("500x750")
        self.root.resizable(True, True)
        
        # تنسيق الألوان
        self.bg_color = "#f0f8ff"
        self.fg_color = "#2c3e50"
        self.accent_color = "#3498db"
        self.prayer_color = "#2980b9"
        self.algeria_green = "#006633"
        self.algeria_red = "#d21034"
        
        self.root.configure(bg=self.bg_color)
        
        # إعداد المتغيرات
        self.wilayas = self.load_wilayas()
        self.cities = self.load_cities()
        
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
            "عنابة", "قالمة", "قسنطينة", "المدية", "مستغانم", "المسيلة", "معسكر", "ورقلة",
            "أم البواقي", "البيض", "إليزي", "برج بوعريريج", "بومرداس", "الطارف", "تندوف",
            "تيسمسيلت", "الوادي", "خنشلة", "سوق أهراس", "تيبازة", "ميلة", "عين الدفلى",
            "النعامة", "عين تيموشنت", "غرداية", "غليزان", "تمنراست"
        ]
        return sorted(wilayas)
    
    def load_cities(self):
        """تحميل المدن لكل ولاية"""
        cities_by_wilaya = {
            "الجزائر": ["الجزائر الوسطى", "القبة", "باب الوادي", "الحراش", "بولوغين", "الدار البيضاء", "براقي"],
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
            "تيبازة": ["تيبازة", "شرشال", "دamous", "فوكة", "حجوط"],
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
        
        # علم الجزائر رمزياً
        colors_frame = tk.Frame(title_frame, bg=self.bg_color)
        colors_frame.pack()
        
        tk.Frame(colors_frame, bg=self.algeria_green, width=100, height=20).pack(side=tk.LEFT, padx=2)
        tk.Frame(colors_frame, bg="white", width=100, height=20).pack(side=tk.LEFT, padx=2)
        tk.Frame(colors_frame, bg=self.algeria_red, width=100, height=20).pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            title_frame, 
            text="مواقيت الصلاة في الجزائر", 
            font=("Arial", 22, "bold"),
            bg=self.bg_color,
            fg=self.algeria_green
        ).pack(pady=10)
        
        # إطار اختيار الموقع
        location_frame = tk.Frame(self.root, bg=self.bg_color)
        location_frame.pack(pady=15, padx=20, fill=tk.X)
        
        # اختيار الولاية
        tk.Label(
            location_frame, 
            text="الولاية:", 
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.wilaya_combo = ttk.Combobox(
            location_frame, 
            values=self.wilayas,
            state="readonly",
            font=("Arial", 13),
            width=25
        )
        self.wilaya_combo.grid(row=0, column=1, padx=5, pady=5)
        self.wilaya_combo.bind("<<ComboboxSelected>>", self.on_wilaya_selected)
        
        # اختيار المدينة
        tk.Label(
            location_frame, 
            text="المدينة:", 
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.city_combo = ttk.Combobox(
            location_frame, 
            state="readonly",
            font=("Arial", 13),
            width=25
        )
        self.city_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # تاريخ اليوم
        self.date_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14),
            bg=self.bg_color,
            fg=self.algeria_red
        )
        self.date_label.pack(pady=10)
        
        # زر الحصول على مواقيت الصلاة
        self.get_times_btn = tk.Button(
            self.root,
            text="عرض مواقيت الصلاة",
            font=("Arial", 14, "bold"),
            bg=self.algeria_green,
            fg="white",
            command=self.get_prayer_times,
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.get_times_btn.pack(pady=15)
        
        # إطار عرض مواقيت الصلاة
        self.times_frame = tk.Frame(self.root, bg=self.bg_color)
        self.times_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # تسميات مواقيت الصلاة
        prayers = ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"]
        self.prayer_labels = {}
        self.time_labels = {}
        
        for i, prayer in enumerate(prayers):
            # إطار لكل صلاة
            prayer_frame = tk.Frame(self.times_frame, bg=self.bg_color)
            prayer_frame.pack(fill=tk.X, pady=8)
            
            # اسم الصلاة
            self.prayer_labels[prayer] = tk.Label(
                prayer_frame,
                text=prayer,
                font=("Arial", 16, "bold"),
                bg=self.bg_color,
                fg=self.prayer_color,
                width=10,
                anchor=tk.W
            )
            self.prayer_labels[prayer].pack(side=tk.LEFT, padx=10)
            
            # وقت الصلاة
            self.time_labels[prayer] = tk.Label(
                prayer_frame,
                text="--:--",
                font=("Arial", 16, "bold"),
                bg=self.bg_color,
                fg=self.fg_color
            )
            self.time_labels[prayer].pack(side=tk.RIGHT, padx=10)
        
        # إطار الوقت الحالي
        current_time_frame = tk.Frame(self.root, bg=self.bg_color)
        current_time_frame.pack(pady=10)
        
        self.current_time_label = tk.Label(
            current_time_frame,
            text="",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.algeria_red
        )
        self.current_time_label.pack()
        
        # تحديث الوقت الحالي
        self.update_current_time()
        
        # معلومات التطبيق
        info_label = tk.Label(
            self.root,
            text="تطبيق مواقيت الصلاة للولايات الجزائرية\nAPI: Aladhan.com",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="gray"
        )
        info_label.pack(pady=10)
    
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
        # الحصول على توقيت الجزائر (توقيت وسط أوروبا +1)
        try:
            tz = pytz.timezone('Africa/Algiers')
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            self.current_time_label.config(text=f"التاريخ والوقت الحالي: {current_time}")
        except:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.current_time_label.config(text=f"التاريخ والوقت الحالي: {current_time}")
        
        # تحديث التاريخ
        hijri_date = self.get_hijri_date()
        gregorian_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label.config(text=f"التاريخ الميلادي: {gregorian_date}\nالتاريخ الهجري: {hijri_date}")
        
        # تحديث كل ثانية
        self.root.after(1000, self.update_current_time)
    
    def get_hijri_date(self):
        """الحصول على التاريخ الهجري"""
        try:
            # استخدام API للحصول على التاريخ الهجري
            today = datetime.now().strftime("%d-%m-%Y")
            response = requests.get(f"http://api.aladhan.com/v1/gToH?date={today}")
            if response.status_code == 200:
                data = response.json()
                hijri_date = data['data']['hijri']['date']
                hijri_day = data['data']['hijri']['day']
                hijri_month = data['data']['hijri']['month']['ar']
                hijri_year = data['data']['hijri']['year']
                return f"{hijri_day} {hijri_month} {hijri_year}"
        except:
            pass
        return "---"
    
    def get_prayer_times(self):
        """الحصول على مواقيت الصلاة من API"""
        wilaya = self.wilaya_combo.get()
        city = self.city_combo.get()
        
        if not wilaya or not city:
            messagebox.showwarning("تحذير", "الرجاء اختيار الولاية والمدينة")
            return
        
        try:
            # استخدام API Aladhan.com
            today = datetime.now().strftime("%d-%m-%Y")
            
            # البحث باستخدام اسم المدينة
            response = requests.get(f"http://api.aladhan.com/v1/timingsByCity/{today}?city={city}&country=Algeria&method=2")
            
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
                    
                    for prayer, time in prayer_times.items():
                        self.time_labels[prayer].config(text=time)
                    
                    # تحديث العنوان
                    self.root.title(f"مواقيت الصلاة في {city}, {wilaya}")
                    
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
            
            for prayer, time in default_times.items():
                self.time_labels[prayer].config(text=time)
            
            messagebox.showinfo("ملاحظة", "تم عرض أوقات افتراضية. تحقق من اتصالك بالإنترنت للحصول على الأوقات الدقيقة.")

def main():
    root = tk.Tk()
    app = AlgeriaPrayerTimesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
