# Project: Tesla Ultimate Widget
# Author: avcar20 (Github)
# Copyright (C) 2026 avcar20
# Licensed under the GNU GPLv3

import tkinter as tk
import paho.mqtt.client as mqtt
import threading
import signal
import sys
import time
from plyer import notification

# --- AYARLAR ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
ELECTRICITY_PRICE = 3.45  # Elektrik birim fiyatı

# --- KONUM AYARI ---
WIDGET_X = 10  
WIDGET_Y_OFFSET = 48 

# Veri Saklama
data = {
    "battery": "--",
    "range": "--",
    "in_temp": "--",
    "out_temp": "--",
    "charging_state": "Disconnected",
    "charge_power": "0",
    "time_left": "0.0",
    "energy_added": "0"
}

# Durum Takibi
state_tracker = {
    "locked": True,
    "doors_open": False,
    "battery_notified": False,
    "user_present_notified": False
}

# --- BİLDİRİM FONKSİYONU ---
def send_notification(title, message):
    print(f"🔔 GÖNDERİLİYOR: {title} - {message}") # Konsoldan takip et
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Tesla Monitor',
            timeout=5 # Ekranda kalma süresi
        )
    except Exception as e:
        print(f"Bildirim hatası: {e}")

# --- PENCERE AYARLARI ---
def create_window():
    root = tk.Tk()
    root.title("Tesla Ultimate Widget")
    
    bg_color = '#101010'
    root.configure(bg=bg_color)
    root.overrideredirect(True)
    root.attributes('-topmost', True)

    screen_h = root.winfo_screenheight()
    root.geometry(f"+{WIDGET_X}+{screen_h - WIDGET_Y_OFFSET}")

    # --- ARAYÜZ TASARIMI ---
    container = tk.Frame(root, bg=bg_color)
    container.pack(fill="both", expand=True, padx=8, pady=4)

    font_style = ("Segoe UI", 10, "bold") 

    # === SOL BLOK (Standart Bilgiler) ===
    frame_left = tk.Frame(container, bg=bg_color)
    frame_left.pack(side="left", fill="y")

    # -- Sol Üst (Pil | Menzil) --
    frame_left_top = tk.Frame(frame_left, bg=bg_color)
    frame_left_top.pack(side="top", anchor="w")
    
    # Pil
    lbl_battery = tk.Label(frame_left_top, text="🔋%--", font=font_style, bg=bg_color, fg="#00ff00")
    lbl_battery.pack(side="left")
    
    tk.Label(frame_left_top, text=" | ", font=font_style, bg=bg_color, fg="#555").pack(side="left")
    
    # Menzil (Bayrak Simgesi - Bitişik)
    lbl_range = tk.Label(frame_left_top, text="🏁-- km", font=font_style, bg=bg_color, fg="white")
    lbl_range.pack(side="left", padx=(0,0)) 
    
    # -- Sol Alt (İç | Dış Sıcaklık) --
    frame_left_bottom = tk.Frame(frame_left, bg=bg_color)
    frame_left_bottom.pack(side="top", anchor="w")

    # İç Sıcaklık (Ev Simgesi - Bitişik)
    lbl_in_combined = tk.Label(frame_left_bottom, text="🏠--°", font=font_style, bg=bg_color, fg="#00bfff")
    lbl_in_combined.pack(side="left", padx=(0,0))
    
    tk.Label(frame_left_bottom, text=" | ", font=font_style, bg=bg_color, fg="#555").pack(side="left")

    # Dış Sıcaklık (Ağaç Simgesi - Bitişik)
    lbl_out_combined = tk.Label(frame_left_bottom, text="🌲--°", font=font_style, bg=bg_color, fg="#aaaaaa")
    lbl_out_combined.pack(side="left", padx=(0,0))

    # === SAĞ BLOK (Şarj Bilgileri - 4x2 Grid) ===
    frame_charge = tk.Frame(container, bg=bg_color)
    
    # --- 1. SATIR (Güç | Fiyat) ---
    lbl_sep_1 = tk.Label(frame_charge, text=" | ", font=font_style, bg=bg_color, fg="#555")
    lbl_sep_1.grid(row=0, column=0, sticky="w")
    
    lbl_power = tk.Label(frame_charge, text="⚡ -- kW", font=font_style, bg=bg_color, fg="#ffd700")
    lbl_power.grid(row=0, column=1, sticky="w")
    
    lbl_sep_price = tk.Label(frame_charge, text=" | ", font=font_style, bg=bg_color, fg="#555")
    lbl_sep_price.grid(row=0, column=2, sticky="w")
    
    lbl_cost = tk.Label(frame_charge, text="💰 -- ₺", font=font_style, bg=bg_color, fg="#00ff7f")
    lbl_cost.grid(row=0, column=3, sticky="w")

    # --- 2. SATIR (Süre | Eklenen Enerji) ---
    lbl_sep_2 = tk.Label(frame_charge, text=" | ", font=font_style, bg=bg_color, fg="#555")
    lbl_sep_2.grid(row=1, column=0, sticky="w")
    
    lbl_time = tk.Label(frame_charge, text="⏳ --", font=font_style, bg=bg_color, fg="#ffd700")
    lbl_time.grid(row=1, column=1, sticky="w")
    
    lbl_sep_energy = tk.Label(frame_charge, text=" | ", font=font_style, bg=bg_color, fg="#555")
    lbl_sep_energy.grid(row=1, column=2, sticky="w")
    
    lbl_energy = tk.Label(frame_charge, text="📥 -- kWh", font=font_style, bg=bg_color, fg="#ff00ff") 
    lbl_energy.grid(row=1, column=3, sticky="w")

    # --- KAPATMA İŞLEMLERİ ---
    def on_close(sig=None, frame=None):
        print("\nSistem kapatılıyor...")
        root.destroy()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_close)
    root.bind('<Double-Button-1>', lambda e: on_close())

    def check_signals():
        root.after(500, check_signals)
    root.after(500, check_signals)

    # --- ARAYÜZ GÜNCELLEME (LOOP) ---
    def update_ui():
        try:
            # 1. Standart Veriler
            if data['battery'] != "--" and int(data['battery']) < 20:
                lbl_battery.config(fg="red")
            else:
                lbl_battery.config(fg="#00ff00")

            lbl_battery.config(text=f"🔋%{data['battery']}")
            
            # GÜNCELLEMELER (Bitişik format)
            lbl_range.config(text=f"🏁{data['range']} km") 
            lbl_in_combined.config(text=f"🏠{data['in_temp']}°")
            lbl_out_combined.config(text=f"🌲{data['out_temp']}°")

            # 2. Şarj Paneli Mantığı
            if data['charging_state'] == "Charging":
                frame_charge.pack(side="left", fill="y", anchor="w")
                
                # Güç
                lbl_power.config(text=f"⚡ {data['charge_power']} kW")
                
                # Süre
                try:
                    hours_left = float(data['time_left'])
                    saat = int(hours_left)
                    dakika = int((hours_left - saat) * 60)
                    time_str = f"{saat}sa {dakika}dk"
                except:
                    time_str = "--"
                lbl_time.config(text=f"⏳ {time_str}")

                # Enerji ve Maliyet
                try:
                    energy = float(data['energy_added'])
                    cost = energy * ELECTRICITY_PRICE
                    
                    lbl_cost.config(text=f"💰 {cost:.2f} ₺")
                    lbl_energy.config(text=f"📥 {energy:.1f} kWh")
                except:
                    lbl_cost.config(text="💰 0.00 ₺")
                    lbl_energy.config(text="📥 0.0 kWh")
            else:
                frame_charge.pack_forget()

            root.lift()
            root.attributes('-topmost', True)

        except Exception as e:
            print(f"UI Hatası: {e}")
        
        root.after(1000, update_ui)

    # --- MQTT MANTIK ---
    def on_message(client, userdata, msg):
        topic = msg.topic.split("/")[-1]
        payload = msg.payload.decode("utf-8")
        
        # Pil Durumu
        if topic == "battery_level":
            data["battery"] = payload
            try:
                level = int(payload)
                if level == 100 and not state_tracker["battery_notified"]:
                    send_notification("Şarj Tamamlandı! 🔋", "Aracınız %100 doldu.")
                    state_tracker["battery_notified"] = True
                elif level < 100:
                    state_tracker["battery_notified"] = False
            except: pass

        elif topic == "rated_battery_range_km":
            try: data["range"] = str(round(float(payload)))
            except: pass

        elif topic == "inside_temp": data["in_temp"] = payload
        elif topic == "outside_temp": data["out_temp"] = payload
        
        # Kilit Durumu
        elif topic == "locked": 
            state_tracker["locked"] = (payload == "true")
        
        # Şarj Konuları
        elif topic == "charging_state": data["charging_state"] = payload
        elif topic == "charger_power": data["charge_power"] = payload
        elif topic == "time_to_full_charge": data["time_left"] = payload
        elif topic == "charge_energy_added": data["energy_added"] = payload

        # --- BİLDİRİM MANTIĞI (GÜNCELLENDİ) ---
        elif topic == "doors_open":
            is_open = (payload == "true")
            
            # Sadece kapı durumu değiştiğinde (Kapalı -> Açık) işlem yap
            if is_open and not state_tracker["doors_open"]:
                if state_tracker["locked"]:
                    # Araç KİLİTLİ ve kapı açıldıysa -> KRİTİK UYARI
                    send_notification("🚨 GÜVENLİK İHLALİ!", "Araç KİLİTLİ iken kapı açıldı!")
                else:
                    # Araç AÇIK ve kapı açıldıysa -> BİLGİ (Test için önemli)
                    send_notification("🚪 Kapı Açıldı", "Araç kapısı açıldı.")
            
            state_tracker["doors_open"] = is_open

        elif topic == "is_user_present":
            is_present = (payload == "true")
            # Kilitliyken biri araca dokunduysa (User Present olduysa)
            if is_present and state_tracker["locked"] and not state_tracker["user_present_notified"]:
                send_notification("⚠️ Hareket Algılandı!", "Araç kilitli ancak başında biri var.")
                state_tracker["user_present_notified"] = True
            elif not is_present:
                state_tracker["user_present_notified"] = False

    def start_mqtt():
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = lambda c, u, f, rc, p=None: c.subscribe("teslamate/cars/#")
        client.on_message = on_message
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except: pass

    threading.Thread(target=start_mqtt, daemon=True).start()
    update_ui()
    root.mainloop()

if __name__ == "__main__":

    create_window()
