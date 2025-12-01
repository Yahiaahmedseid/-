import flet as ft
import requests
from datetime import datetime
import json
import asyncio
from typing import Dict, List

class PrayerTimesAlgeriaApp:
    def __init__(self):
        # بيانات الولايات والمدن
        self.wilayas = self.load_wilayas()
        self.cities = self.load_cities()
        
        # العناصر الرئيسية
        self.selected_wilaya = "الجزائر"
        self.selected_city = "الجزائر"
        
        # متغيرات الوقت
        self.current_timings = {}
        self.hijri_date = ""
        
        # عناصر الواجهة
        self.title = None
        self.wilaya_dropdown = None
        self.city_dropdown = None
        self.get_times_button = None
        self.time_labels = {}
        self.next_prayer_label = None
        self.current_time_label = None
        self.gregorian_date_label = None
        self.hijri_date_label = None
        
    def load_wilayas(self) -> List[str]:
        """تحميل قائمة ولايات الجزائر"""
        wilayas = [
            "الجزائر", "وهران", "قسنطينة", "عنابة", "باتنة", "بجاية", "بسكرة", "بشار",
            "البليدة", "البويرة", "تمنراست", "تبسة", "تلمسان", "تيارت", "تيزي وزو",
            "الجلفة", "جيجل", "سطيف", "سعيدة", "سكيكدة", "سيدي بلعباس",
            "قالمة", "المدية", "مستغانم", "المسيلة", "معسكر", "ورقلة", "أم البواقي", 
            "البيض", "إليزي", "برج بوعريريج", "بومرداس", "الطارف", "تندوف", "تيسمسيلت",
            "الوادي", "خنشلة", "سوق أهراس", "تيبازة", "ميلة", "عين الدفلى", "النعامة",
            "عين تيموشنت", "غرداية", "غليزان"
        ]
        return sorted(set(wilayas))
    
    def load_cities(self) -> Dict[str, List[str]]:
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
    
    def get_prayer_times(self, city: str, country: str = "Algeria") -> Dict:
        """الحصول على مواقيت الصلاة من API"""
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            response = requests.get(
                f"http://api.aladhan.com/v1/timingsByCity/{today}",
                params={
                    "city": city,
                    "country": country,
                    "method": 2  # طريقة جامعة الأزهر
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
        except Exception as e:
            print(f"Error fetching prayer times: {e}")
            return None
    
    def get_hijri_date(self) -> str:
        """الحصول على التاريخ الهجري"""
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            response = requests.get(f"http://api.aladhan.com/v1/gToH?date={today}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                hijri_date = data['data']['hijri']['date']
                return hijri_date
        except:
            pass
        return "---"
    
    def update_next_prayer(self) -> str:
        """تحديث الصلاة التالية"""
        if not self.current_timings:
            return "الصلاة التالية: --"
        
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_hour, current_minute = map(int, current_time.split(":"))
            current_total_minutes = current_hour * 60 + current_minute
            
            prayers_order = ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"]
            next_prayer = None
            min_time_diff = 24 * 60  # عدد الدقائق في اليوم
            
            for prayer in prayers_order:
                if prayer in self.current_timings:
                    prayer_time_str = self.current_timings[prayer]
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
                if hours > 0:
                    time_str = f"بعد {hours} ساعة و {minutes} دقيقة"
                else:
                    time_str = f"بعد {minutes} دقيقة"
                return f"الصلاة التالية: {next_prayer} ({time_str})"
            else:
                return "الصلاة التالية: --"
                
        except Exception as e:
            print(f"Error updating next prayer: {e}")
            return "الصلاة التالية: --"
    
    async def update_time_display(self, page: ft.Page):
        """تحديث الوقت الحالي وعرضه"""
        while True:
            try:
                # تحديث الوقت الحالي
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                gregorian_date = now.strftime("%Y-%m-%d")
                
                # تحديث التاريخ الهجري كل دقيقة
                if now.second == 0 or not self.hijri_date:
                    self.hijri_date = self.get_hijri_date()
                
                # تحديث العناصر
                if self.current_time_label:
                    self.current_time_label.value = f"⏰ الوقت الحالي: {current_time}"
                
                if self.gregorian_date_label:
                    self.gregorian_date_label.value = f"📅 التاريخ الميلادي: {gregorian_date}"
                
                if self.hijri_date_label:
                    self.hijri_date_label.value = f"🌙 التاريخ الهجري: {self.hijri_date}"
                
                # تحديث الصلاة التالية
                if self.next_prayer_label:
                    self.next_prayer_label.value = self.update_next_prayer()
                
                # تحديث الصفحة
                if page:
                    page.update()
                    
            except Exception as e:
                print(f"Error updating time display: {e}")
            
            # انتظر ثانية واحدة
            await asyncio.sleep(1)
    
    def on_wilaya_change(self, e):
        """عند تغيير الولاية"""
        self.selected_wilaya = e.control.value
        if self.selected_wilaya in self.cities:
            cities_list = self.cities[self.selected_wilaya]
            self.city_dropdown.options = [
                ft.dropdown.Option(city) for city in cities_list
            ]
            if cities_list:
                self.city_dropdown.value = cities_list[0]
                self.selected_city = cities_list[0]
            self.city_dropdown.update()
    
    def on_city_change(self, e):
        """عند تغيير المدينة"""
        self.selected_city = e.control.value
    
    async def on_get_times_click(self, e, page: ft.Page):
        """عند النقر على زر الحصول على مواقيت الصلاة"""
        if not self.selected_wilaya or not self.selected_city:
            page.snack_bar = ft.SnackBar(ft.Text("الرجاء اختيار الولاية والمدينة"))
            page.snack_bar.open = True
            page.update()
            return
        
        # تغيير نص الزر أثناء التحميل
        self.get_times_button.text = "⏳ جاري التحميل..."
        self.get_times_button.disabled = True
        page.update()
        
        try:
            # الحصول على مواقيت الصلاة
            data = self.get_prayer_times(self.selected_city)
            
            if data and 'data' in data and 'timings' in data['data']:
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
                
                # تحديث التسميات
                for prayer, time in prayer_times.items():
                    if prayer in self.time_labels:
                        self.time_labels[prayer].value = time
                
                # تحديث التاريخ الهجري
                if 'date' in data['data'] and 'hijri' in data['data']['date']:
                    self.hijri_date = data['data']['date']['hijri']['date']
                    if self.hijri_date_label:
                        self.hijri_date_label.value = f"🌙 التاريخ الهجري: {self.hijri_date}"
                
                # إظهار رسالة نجاح
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ تم تحميل مواقيت الصلاة لـ {self.selected_city}, {self.selected_wilaya}"))
                page.snack_bar.open = True
                
                # تحديث عنوان الصفحة
                page.title = f"🇩🇿 مواقيت الصلاة في {self.selected_city}, {self.selected_wilaya}"
                
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ تعذر الحصول على مواقيت الصلاة. تأكد من اتصال الإنترنت."))
                page.snack_bar.open = True
                
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطأ: {str(ex)}"))
            page.snack_bar.open = True
            
            # عرض أوقات افتراضية لأغراض الاختبار
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
                if prayer in self.time_labels:
                    self.time_labels[prayer].value = time
        
        finally:
            # إعادة نص الزر إلى وضعه الطبيعي
            self.get_times_button.text = "🕌 احصل على مواقيت الصلاة"
            self.get_times_button.disabled = False
            page.update()
    
    def build(self, page: ft.Page):
        """بناء واجهة التطبيق"""
        # إعدادات الصفحة
        page.title = "🇩🇿 تطبيق مواقيت الصلاة في الجزائر"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        
        # ألوان التطبيق
        primary_color = "#006633"  # أخضر العلم الجزائري
        secondary_color = "#d21034"  # أحمر العلم الجزائري
        accent_color = "#f0f8ff"
        
        # عنوان التطبيق
        self.title = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("🇩🇿", size=40),
                                margin=ft.margin.only(right=10)
                            ),
                            ft.Column(
                                [
                                    ft.Text("تطبيق مواقيت الصلاة", size=28, weight=ft.FontWeight.BOLD, color=primary_color),
                                    ft.Text("في الجزائر", size=20, color=secondary_color),
                                ]
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # علم الجزائر
                    ft.Row(
                        [
                            ft.Container(width=100, height=20, bgcolor=primary_color, border_radius=5),
                            ft.Container(width=100, height=20, bgcolor="white", border_radius=5),
                            ft.Container(width=100, height=20, bgcolor=secondary_color, border_radius=5),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            margin=ft.margin.only(bottom=20)
        )
        
        # إطار اختيار الموقع
        location_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📍 اختر موقعك", size=18, weight=ft.FontWeight.BOLD, color=primary_color),
                        
                        ft.Row(
                            [
                                ft.Text("الولاية:", size=16, width=100),
                                self.wilaya_dropdown = ft.Dropdown(
                                    width=300,
                                    options=[ft.dropdown.Option(wilaya) for wilaya in self.wilayas],
                                    value="الجزائر",
                                    on_change=self.on_wilaya_change,
                                    border_color=primary_color,
                                    filled=True
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START
                        ),
                        
                        ft.Row(
                            [
                                ft.Text("المدينة:", size=16, width=100),
                                self.city_dropdown = ft.Dropdown(
                                    width=300,
                                    options=[ft.dropdown.Option(city) for city in self.cities["الجزائر"]],
                                    value="الجزائر",
                                    on_change=self.on_city_change,
                                    border_color=primary_color,
                                    filled=True
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START
                        ),
                        
                        ft.Container(height=10),
                        
                        self.get_times_button = ft.ElevatedButton(
                            text="🕌 احصل على مواقيت الصلاة",
                            icon="mosque",
                            on_click=lambda e: self.on_get_times_click(e, page),
                            style=ft.ButtonStyle(
                                bgcolor=primary_color,
                                color="white",
                                padding=20
                            ),
                            width=300
                        )
                    ],
                    spacing=15
                ),
                padding=20
            ),
            elevation=5
        )
        
        # إطار معلومات التاريخ والوقت
        date_time_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📅 معلومات اليوم", size=18, weight=ft.FontWeight.BOLD, color=primary_color),
                        
                        self.gregorian_date_label = ft.Text(
                            "📅 التاريخ الميلادي: --/--/----",
                            size=14
                        ),
                        
                        self.hijri_date_label = ft.Text(
                            "🌙 التاريخ الهجري: --/--/----",
                            size=14,
                            color=secondary_color
                        ),
                        
                        self.current_time_label = ft.Text(
                            "⏰ الوقت الحالي: --:--:--",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=primary_color
                        ),
                    ],
                    spacing=10
                ),
                padding=20
            ),
            elevation=3
        )
        
        # إطار مواقيت الصلاة
        prayer_times_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("🕌 مواقيت الصلاة", size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                        
                        # قائمة مواقيت الصلاة
                        self.create_prayer_time_row("🌅 الفجر", "الفجر"),
                        ft.Divider(height=1),
                        
                        self.create_prayer_time_row("☀️ الشروق", "الشروق"),
                        ft.Divider(height=1),
                        
                        self.create_prayer_time_row("🕛 الظهر", "الظهر"),
                        ft.Divider(height=1),
                        
                        self.create_prayer_time_row("🕒 العصر", "العصر"),
                        ft.Divider(height=1),
                        
                        self.create_prayer_time_row("🌇 المغرب", "المغرب"),
                        ft.Divider(height=1),
                        
                        self.create_prayer_time_row("🌙 العشاء", "العشاء"),
                        
                        ft.Container(height=20),
                        
                        # الصلاة التالية
                        self.next_prayer_label = ft.Container(
                            content=ft.Text(
                                "الصلاة التالية: --",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                                text_align=ft.TextAlign.CENTER
                            ),
                            bgcolor=primary_color,
                            padding=15,
                            border_radius=10,
                            alignment=ft.alignment.center
                        )
                    ],
                    spacing=10
                ),
                padding=20
            ),
            elevation=5
        )
        
        # معلومات التطبيق
        footer = ft.Container(
            content=ft.Column(
                [
                    ft.Divider(),
                    ft.Text(
                        "تطبيق مواقيت الصلاة للولايات الجزائرية\nAPI: Aladhan.com",
                        size=12,
                        color="gray",
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            margin=ft.margin.only(top=20)
        )
        
        # تجميع كل العناصر في صفحة واحدة
        page.add(
            self.title,
            location_card,
            date_time_card,
            prayer_times_card,
            footer
        )
        
        # بدء مهمة تحديث الوقت
        asyncio.create_task(self.update_time_display(page))
        
        # الحصول على مواقيت الصلاة الافتراضية عند البدء
        asyncio.create_task(self.on_get_times_click(None, page))
    
    def create_prayer_time_row(self, prayer_name: str, prayer_key: str):
        """إنشاء صف لعرض وقت صلاة"""
        time_text = ft.Text("--:--", size=18, weight=ft.FontWeight.BOLD, width=80)
        self.time_labels[prayer_key] = time_text
        
        return ft.Row(
            [
                ft.Text(prayer_name, size=18, weight=ft.FontWeight.BOLD, width=150),
                ft.Container(expand=True),
                time_text
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

def main(page: ft.Page):
    """الدالة الرئيسية للتطبيق"""
    app = PrayerTimesAlgeriaApp()
    app.build(page)

if __name__ == "__main__":
    # تشغيل التطبيق
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,  # يمكن تغييرها إلى ft.AppView.WEB_BROWSER للويب
        port=8550,
        assets_dir="assets"
    )
