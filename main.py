import asyncio
import edge_tts
from customtkinter import *
from pydub import AudioSegment
from pygame import mixer
import re
from dotenv import load_dotenv
import os

os.makedirs("fragments", exist_ok=True)
os.makedirs("output", exist_ok=True)

load_dotenv()
ffmpeg_path = os.getenv("FFMPEG_PATH")

AudioSegment.converter = ffmpeg_path

# === USTAWIENIA WSTĘPNE ===
set_appearance_mode("dark")
set_default_color_theme("green")

app = CTk()
app.title("Narrator Studio")
app.geometry("1200x1050")

fragments = []
max_chars = 2500
mixer.init()

# === MAPA LEKTORÓW ===
LEKTORZY = {
    "Marek": "pl-PL-MarekNeural",
    "Zofia": "pl-PL-ZofiaNeural",}

# === FUNKCJA GENERUJĄCA GŁOS ===
def tts_generate(text, voice_id, filename, tempo="+0%"):
    async def run():
        communicate = edge_tts.Communicate(text=text, voice=voice_id, rate=tempo)
        await communicate.save(filename)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.close()

# === KONFIGURACJA ===
config_frame = CTkFrame(app)
config_frame.pack(pady=20)

voice_label = CTkLabel(config_frame, text="Lektor:")
voice_label.grid(row=0, column=0, padx=10, pady=(10, 10))
voice_option = CTkOptionMenu(config_frame, values=list(LEKTORZY.keys()), command=lambda _: enable_all_save_buttons())
voice_option.set("Marek")
voice_option.grid(row=0, column=1, pady=(0, 10))

tempo_label = CTkLabel(config_frame, text="Tempo mowy (-30 do 30):")
tempo_label.grid(row=0, column=2, padx=10, pady=(0, 10))

tempo_value = StringVar(value="0")
tempo_slider = CTkSlider(config_frame, from_=-30, to=30, number_of_steps=60,
                         command=lambda v: [tempo_value.set(str(int(float(v)))), enable_all_save_buttons()])

tempo_slider.set(0)
tempo_slider.grid(row=0, column=3, pady=(0, 10))
tempo_value_label = CTkLabel(config_frame, textvariable=tempo_value)
tempo_value_label.grid(row=0, column=4, pady=(0, 10))

music_label = CTkLabel(config_frame, text="Podkład:")
music_label.grid(row=1, column=0, padx=10, pady=(10, 10))
background_folder = "backgrounds"
background_files = [
    f[:-4] for f in os.listdir(background_folder) if f.endswith(".mp3")
]

music_option = CTkOptionMenu(
    config_frame,
    values=["NO BACKGROUND"] + background_files
)
music_option.set("NO BACKGROUND")

music_option.set("BRAK PODKŁADU")
music_option.grid(row=1, column=1, pady=(10, 10))


voice_option.configure(command=lambda _: enable_all_save_buttons())
music_option.configure(command=lambda _: enable_all_save_buttons())


fadein_label = CTkLabel(config_frame, text="Fade in(s):")
fadein_label.grid(row=1, column=2, padx=10)
fadein_entry = CTkEntry(config_frame, width=50)
fadein_entry.insert(0, "3")
fadein_entry.grid(row=1, column=3)

fadeout_label = CTkLabel(config_frame, text="Fade out (s):")
fadeout_label.grid(row=1, column=4, padx=10)
fadeout_entry = CTkEntry(config_frame, width=50)
fadeout_entry.insert(0, "3")
fadeout_entry.grid(row=1, column=5)

start_delay_label = CTkLabel(config_frame, text="Start lektora (s):")
start_delay_label.grid(row=2, column=0, padx=10, pady=(10, 10))
start_delay_entry = CTkEntry(config_frame, width=50)
start_delay_entry.insert(0, "0")
start_delay_entry.grid(row=2, column=1)

end_delay_label = CTkLabel(config_frame, text="Koniec lektora (s):")
end_delay_label.grid(row=2, column=2, padx=10)
end_delay_entry = CTkEntry(config_frame, width=50)
end_delay_entry.insert(0, "0")
end_delay_entry.grid(row=2, column=3)

fadein_entry.bind("<FocusOut>", lambda e: enable_all_save_buttons())
fadeout_entry.bind("<FocusOut>", lambda e: enable_all_save_buttons())
start_delay_entry.bind("<FocusOut>", lambda e: enable_all_save_buttons())
end_delay_entry.bind("<FocusOut>", lambda e: enable_all_save_buttons())


volume_label = CTkLabel(config_frame, text="Głośność podkładu (%):")
volume_label.grid(row=3, column=0, padx=10, pady=(10, 10))

volume_value = StringVar(value="50")
volume_slider = CTkSlider(config_frame, from_=0, to=150, number_of_steps=150,
                          command=lambda v: [volume_value.set(str(int(float(v)))), enable_all_save_buttons()])
volume_slider.set(50)
volume_slider.grid(row=3, column=1, columnspan=2, sticky="we", pady=(10, 10))

volume_display = CTkLabel(config_frame, textvariable=volume_value)
volume_display.grid(row=3, column=3, padx=(5, 10), pady=(10, 10))


# === OBSŁUGA FRAGMENTÓW ===
def update_counter(textbox, label, save_button, original_text):
    text = textbox.get("0.0", "end").strip()
    count = len(text)
    label.configure(text=f"Licznik: {count}", text_color="red" if count > max_chars else "black")
    save_button.configure(state=NORMAL if text != original_text.get() else DISABLED,
                          text="Zapisz zmiany" if text != original_text.get() else "Zapisz")

def parse_text_with_pauses(text, output_filename):
    parts = re.split(r'(\{pauza=\d+\})', text)
    segments = []

    for idx, part in enumerate(parts):
        if match := re.match(r'\{pauza=(\d+)\}', part):
            pause_duration = int(match.group(1)) * 1000
            segments.append(AudioSegment.silent(duration=pause_duration))
        elif part.strip():
            temp_filename = f"_temp_{idx}.mp3"
            tempo_val = int(tempo_slider.get())
            tempo_str = f"+{tempo_val}%" if tempo_val >= 0 else f"{tempo_val}%"
            tts_generate(
                text=part.strip(),
                voice_id=LEKTORZY[voice_option.get()],
                filename=temp_filename,
                tempo=tempo_str
            )
            segment = AudioSegment.from_file(temp_filename)
            segments.append(segment)
            os.remove(temp_filename)

    final_audio = sum(segments)
    final_audio.export(output_filename, format="mp3")

def enable_all_save_buttons():
    for child in scrollable_frame.winfo_children():
        for widget in child.winfo_children():
            if isinstance(widget, CTkButton) and widget.cget("text") in ["Zapisz", "Zapisz zmiany"]:
                widget.configure(state=NORMAL)


def save_fragment(filepath, textbox, info_label, save_button, original_text):
    text = textbox.get("0.0", "end").strip()
    if not text:
        return

    mixer.music.stop()
    try:
        mixer.music.unload()
    except:
        pass

    if os.path.exists(filepath):
        os.remove(filepath)  # force overwrite

    parse_text_with_pauses(text, filepath)
    original_text.set(text)
    info_label.configure(text=f"Zapisano jako {filepath}")
    save_button.configure(state=DISABLED, text="Zapisz")


def play_fragment(filepath):
    if os.path.exists(filepath):
        mixer.music.stop()
        try:
            mixer.music.unload()
        except:
            pass
        mixer.music.load(filepath)
        mixer.music.play()


def play_final():
    filename = output_name_entry.get().strip()
    if filename:
        filepath = os.path.join("output", f"{filename}.mp3")
        if os.path.exists(filepath):
            mixer.music.stop()
            try:
                mixer.music.unload()
            except:
                pass
            mixer.music.load(filepath)
            mixer.music.play()

def insert_pause(textbox, seconds):
    textbox.insert("insert", f"{{pauza={seconds}}}")


def add_fragment():
    index = len(fragments) + 1
    fragment_path = os.path.join("fragments", f"fragment{index}.mp3")
    frame = CTkFrame(scrollable_frame)
    frame.pack(pady=10, fill="x")

    label = CTkLabel(frame, text=f"Fragment {index}")
    label.pack(anchor="w", padx=10)

    textbox = CTkTextbox(frame, height=120, wrap="word")
    textbox.pack(padx=10, pady=5, fill="x")

    counter = CTkLabel(frame, text="Licznik: 0")
    counter.pack(anchor="e", padx=10)

    original_text = StringVar()
    info_label = CTkLabel(frame, text="")
    info_label.pack(padx=10, pady=2, anchor="w")

    pause_menu = CTkOptionMenu(
        frame,
        width=120,
        values=["⏸️ 1 sek", "⏸️ 2 sek", "⏸️ 3 sek", "⏸️ 5 sek", "⏸️ 10 sek"],
        command=lambda value: insert_pause(textbox, int(value.split()[1])),
    )
    pause_menu.set("➕ Pauza")
    pause_menu.pack(side="left", padx=10, pady=5)
    pause_menu.configure(button_color="#d9534f", button_hover_color="#c9302c")

    save_btn = CTkButton(
        frame,
        text="Zapisz",
        command=lambda: save_fragment(fragment_path, textbox, info_label, save_btn, original_text),
        state=DISABLED
    )
    save_btn.pack(side="right", padx=10, pady=5)

    play_btn = CTkButton(
        frame,
        text="Przesłuchaj",
        command=lambda: play_fragment(fragment_path)
    )
    play_btn.pack(side="right", padx=10, pady=5)

    textbox.bind(
        "<<Modified>>",
        lambda e: [update_counter(textbox, counter, save_btn, original_text), textbox.edit_modified(False)]
    )

    fragments.append((textbox, counter, info_label))

# === ŁĄCZENIE FRAGMENTÓW ===

def join_all_fragments():
    output_name = output_name_entry.get().strip()
    if not output_name:
        return

    fadein = int(float(fadein_entry.get()) * 1000)
    fadeout = int(float(fadeout_entry.get()) * 1000)
    start_delay = int(float(start_delay_entry.get()) * 1000)
    end_delay = int(float(end_delay_entry.get()) * 1000)

    selected_music = music_option.get()
    full_voice_audio = AudioSegment.empty()

    # 🔗 Połącz wszystkie fragmenty lektora
    for i in range(1, len(fragments) + 1):
        filepath = os.path.join("fragments", f"fragment{i}.mp3")
        if os.path.exists(filepath):
            frag = AudioSegment.from_file(filepath)
            full_voice_audio += frag

    # 🧮 Długość całego nagrania = cisza przed + lektor + cisza po
    total_length = start_delay + len(full_voice_audio) + end_delay

    # 🎵 Jeśli wybrano podkład
    if selected_music != "BRAK PODKŁADU":
        music_path = os.path.join("backgrounds", f"{selected_music}.mp3")
        if os.path.exists(music_path):
            music = AudioSegment.from_file(music_path)
            # 🔊 Zastosuj zmianę głośności podkładu
            volume_percent = int(volume_value.get())
            music = music - (100 - volume_percent)  # np. 50% = -50 dB, 100% = 0 dB
            # Zapętl jeśli za krótki
            if len(music) < total_length:
                music = music * (total_length // len(music) + 1)

            # Przytnij dokładnie do długości
            music = music[:total_length]

            # Fade in/out
            music = music.fade_in(fadein).fade_out(fadeout)

            # 🔈 Dodaj ciszę na początku i końcu lektora, a potem nałóż
            voice_with_delay = AudioSegment.silent(duration=start_delay) + full_voice_audio + AudioSegment.silent(duration=end_delay)

            final_mix = music.overlay(voice_with_delay)
        else:
            final_mix = full_voice_audio
    else:
        # Brak podkładu – tylko cisza przed/po
        final_mix = AudioSegment.silent(duration=start_delay) + full_voice_audio + AudioSegment.silent(duration=end_delay)

    # 💾 Zapisz do output/
    output_path = os.path.join("output", f"{output_name}.mp3")
    final_mix.export(output_path, format="mp3")
    join_info.configure(text=f"Zapisano jako output/{output_name}.mp3")


# === GUI ===
scrollable_frame = CTkScrollableFrame(app, width=1000, height=600)
scrollable_frame.pack(pady=20)

# Dodatkowa ramka na dole scrolla
bottom_frame = CTkFrame(scrollable_frame)
bottom_frame.pack(side="bottom", fill="x", pady=10)

add_btn = CTkButton(bottom_frame, text="Dodaj kolejny fragment tekstu", command=add_fragment)
add_btn.pack(pady=50)


output_name_entry = CTkEntry(app, width=300, placeholder_text="Nazwa pliku końcowego")
output_name_entry.pack(pady=5)

join_btn = CTkButton(app, text="Połącz wszystkie fragmenty i dodaj podkład", command=join_all_fragments)
join_btn.pack(pady=5)

play_final_btn = CTkButton(app, text="Przesłuchaj plik końcowy", command=play_final)
play_final_btn.pack(pady=5)

join_info = CTkLabel(app, text="")
join_info.pack(pady=5)

add_fragment()

app.mainloop()
