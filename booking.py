import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import requests
from io import BytesIO

# Expanded Theaters and Movies
theaters = {
    "Cinepolis - Downtown": [
        {"title": "Avengers: Endgame", "time": "7:30 PM", "poster": "https://picsum.photos/200/300?random=1"},
        {"title": "Inception", "time": "9:00 PM", "poster": "https://picsum.photos/200/300?random=2"},
        {"title": "Doctor Strange: Multiverse", "time": "6:00 PM", "poster": "https://picsum.photos/200/300?random=3"},
    ],
    "PVR Cinemas - City Mall": [
        {"title": "Interstellar", "time": "10:30 PM", "poster": "https://picsum.photos/200/300?random=4"},
        {"title": "The Dark Knight", "time": "8:15 PM", "poster": "https://picsum.photos/200/300?random=5"},
        {"title": "Oppenheimer", "time": "5:45 PM", "poster": "https://picsum.photos/200/300?random=6"},
    ],
    "INOX - Grand Plaza": [
        {"title": "Avatar: The Way of Water", "time": "6:45 PM", "poster": "https://picsum.photos/200/300?random=7"},
        {"title": "Spider-Man: No Way Home", "time": "7:45 PM", "poster": "https://picsum.photos/200/300?random=8"},
        {"title": "Frozen II", "time": "4:00 PM", "poster": "https://picsum.photos/200/300?random=9"},
    ],
    "Sathyam Cinemas": [
        {"title": "KGF Chapter 2", "time": "9:15 PM", "poster": "https://picsum.photos/200/300?random=10"},
        {"title": "Pushpa", "time": "7:00 PM", "poster": "https://picsum.photos/200/300?random=11"},
        {"title": "RRR", "time": "10:00 PM", "poster": "https://picsum.photos/200/300?random=12"},
    ],
    "Escape Multiplex": [
        {"title": "Joker", "time": "8:00 PM", "poster": "https://picsum.photos/200/300?random=13"},
        {"title": "The Batman", "time": "9:30 PM", "poster": "https://picsum.photos/200/300?random=14"},
        {"title": "Tenet", "time": "6:30 PM", "poster": "https://picsum.photos/200/300?random=15"},
    ]
}

# Global Variables
selected_theater = None
selected_movie = None
selected_seats = []
selected_date = None
payment_method = None
ticket_file = "ticket.png"

seat_prices = {"Normal": 150, "Premium": 300}


# Main Window
root = tk.Tk()
root.title("🎬 Enchanted Movie Booking 🎟️")
root.geometry("750x750")
root.config(bg="#0f0f0f")

title_label = tk.Label(root, text="🎬 Enchanted Movie Booking 🎟️", 
                       font=("Arial", 18, "bold"), fg="white", bg="#0f0f0f")
title_label.pack(pady=20)


def show_theaters():
    clear_frame()
    tk.Label(root, text="Select a Theater:", font=("Arial", 14, "bold"), fg="cyan", bg="#0f0f0f").pack(pady=10)
    for t in theaters.keys():
        btn = tk.Button(root, text=t, width=40, bg="#1f1f1f", fg="white",
                        command=lambda th=t: select_theater(th))
        btn.pack(pady=5)


def select_theater(theater):
    global selected_theater
    selected_theater = theater
    show_movies()


def show_movies():
    clear_frame()
    tk.Label(root, text=f"Movies at {selected_theater}:", font=("Arial", 14, "bold"), fg="cyan", bg="#0f0f0f").pack(pady=10)
    for m in theaters[selected_theater]:
        btn = tk.Button(root, text=f"{m['title']} ({m['time']})", width=50, bg="#1f1f1f", fg="white",
                        command=lambda mv=m: select_movie(mv))
        btn.pack(pady=5)

    tk.Button(root, text="⬅ Back to Theaters", bg="red", fg="white", command=show_theaters).pack(pady=20)


def select_movie(movie):
    global selected_movie
    selected_movie = movie
    show_dates()


def show_dates():
    clear_frame()
    tk.Label(root, text="Select a Date:", font=("Arial", 14, "bold"), fg="cyan", bg="#0f0f0f").pack(pady=10)

    today = datetime.today()
    for i in range(5):  # next 5 days
        date = today + timedelta(days=i)
        formatted_date = date.strftime("%d %b %Y")
        btn = tk.Button(root, text=formatted_date, width=20, bg="#1f1f1f", fg="white",
                        command=lambda d=formatted_date: select_date(d))
        btn.pack(pady=5)

    tk.Button(root, text="⬅ Back to Movies", bg="red", fg="white", command=show_movies).pack(pady=20)


def select_date(date):
    global selected_date
    selected_date = date
    show_seats()


def show_seats():
    clear_frame()
    tk.Label(root, text=f"{selected_movie['title']} - Select Your Seats", font=("Arial", 14, "bold"), fg="cyan", bg="#0f0f0f").pack(pady=10)

    seats_frame = tk.Frame(root, bg="#0f0f0f")
    seats_frame.pack()

    for i in range(1, 61):  # 60 seats
        seat_type = "Premium" if i > 50 else "Normal"
        color = "gold" if seat_type == "Premium" else "#444"
        btn = tk.Button(seats_frame, text=str(i), width=4, height=2, bg=color, fg="black" if seat_type=="Premium" else "white",
                        command=lambda s=i, st=seat_type: toggle_seat(s, st))
        btn.grid(row=(i-1)//10, column=(i-1)%10, padx=4, pady=4)

    tk.Button(root, text="✅ Proceed to Payment", bg="green", fg="black", command=show_payment).pack(pady=20)
    tk.Button(root, text="⬅ Back to Dates", bg="red", fg="white", command=show_dates).pack()


def toggle_seat(seat, seat_type):
    seat_data = (seat, seat_type)
    if seat_data in selected_seats:
        selected_seats.remove(seat_data)
    else:
        selected_seats.append(seat_data)


def show_payment():
    if not selected_seats:
        messagebox.showwarning("No Seats", "Please select at least one seat!")
        return

    clear_frame()
    total_price = sum(seat_prices[st] for _, st in selected_seats)

    tk.Label(root, text="Select Payment Method:", font=("Arial", 14, "bold"), fg="cyan", bg="#0f0f0f").pack(pady=20)
    tk.Label(root, text=f"Total Price: ₹{total_price}", font=("Arial", 12, "bold"), fg="lime", bg="#0f0f0f").pack(pady=10)

    methods = ["💳 Card", "📱 UPI", "🏦 Net Banking"]
    for method in methods:
        btn = tk.Button(root, text=method, width=30, bg="#1f1f1f", fg="white",
                        command=lambda m=method: confirm_booking(m, total_price))
        btn.pack(pady=10)

    tk.Button(root, text="⬅ Back to Seats", bg="red", fg="white", command=show_seats).pack(pady=20)


def confirm_booking(method, total_price):
    global payment_method, ticket_file
    payment_method = method

    seats_str = ", ".join([f"{num}({typ})" for num, typ in selected_seats])

    ticket_info = (
        f"Theater: {selected_theater}\n"
        f"Movie: {selected_movie['title']} ({selected_movie['time']})\n"
        f"Date: {selected_date}\n"
        f"Seats: {seats_str}\n"
        f"Total: ₹{total_price}\n"
        f"Payment: {payment_method}\n"
        f"Enjoy your show! 🍿"
    )

    qr = qrcode.make(ticket_info)
    qr.save("ticket_qr.png")

    ticket = Image.new("RGB", (500, 450), "white")
    draw = ImageDraw.Draw(ticket)
    font = ImageFont.load_default()

    # Download and paste poster image
    poster_url = selected_movie.get("poster")
    try:
        response = requests.get(poster_url)
        poster_img = Image.open(BytesIO(response.content)).resize((120, 180))
        ticket.paste(poster_img, (20, 250))
    except Exception as e:
        draw.text((20, 250), "[Poster not available]", font=font, fill="red")

    draw.text((160, 20), "🎬 Movie Ticket", font=font, fill="black")
    draw.text((160, 60), ticket_info, font=font, fill="black")

    qr_img = Image.open("ticket_qr.png").resize((120, 120))
    ticket.paste(qr_img, (360, 300))

    ticket.save(ticket_file)

    clear_frame()
    tk.Label(root, text="🎉 Booking Confirmed 🎉", font=("Arial", 16, "bold"), fg="lime", bg="#0f0f0f").pack(pady=20)
    tk.Label(root, text=f"Your ticket has been saved as {ticket_file} ✅", fg="white", bg="#0f0f0f").pack(pady=10)

    tk.Button(root, text="📂 View Ticket", bg="blue", fg="white", command=view_ticket).pack(pady=10)
    tk.Button(root, text="🏠 Back to Theaters", bg="purple", fg="white", command=show_theaters).pack(pady=10)


def view_ticket():
    if os.path.exists(ticket_file):
        Image.open(ticket_file).show()
    else:
        messagebox.showerror("Error", "Ticket file not found!")


def clear_frame():
    for widget in root.winfo_children():
        if widget != title_label:
            widget.destroy()


# Start with Theater Selection
show_theaters()
root.mainloop()
