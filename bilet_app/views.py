import io
import qrcode
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .models import Event, TicketType, Booking, Profil, Category
from .forms import BookingForm, UserUpdateForm, ProfileUpdateForm


# ──────────────────────────────────────────────
# Bosh sahifa — tadbirlar ro'yxati
# ──────────────────────────────────────────────
def event_list(request):
    query    = request.GET.get('q', '')
    cat_id   = request.GET.get('cat', '')
    events   = Event.objects.filter(is_active=True, event_date__gt=timezone.now())
    categories = Category.objects.all()

    if query:
        events = events.filter(title__icontains=query)
    if cat_id:
        events = events.filter(category_id=cat_id)

    return render(request, 'index.html', {
        'events': events,
        'categories': categories,
        'query': query,
        'active_cat': cat_id,
    })


# ──────────────────────────────────────────────
# Tadbir tafsiloti
# ──────────────────────────────────────────────
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    return render(request, 'event_detail.html', {'event': event})


# ──────────────────────────────────────────────
# Bilet bron qilish
# ──────────────────────────────────────────────
@login_required
def book_ticket(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    event = ticket_type.event

    if not ticket_type.is_available:
        messages.error(request, "Bu tur biletlar tugagan.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity > ticket_type.available_seats:
                messages.error(request, f"Faqat {ticket_type.available_seats} ta joy mavjud.")
            else:
                with transaction.atomic():
                    tt = TicketType.objects.select_for_update().get(pk=ticket_type_id)
                    tt.available_seats -= quantity
                    tt.save()

                    booking = form.save(commit=False)
                    booking.user        = request.user
                    booking.ticket_type = tt
                    booking.save()

                return redirect('booking_success', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'book_ticket.html', {
        'form': form,
        'ticket_type': ticket_type,
        'event': event,
    })


# ──────────────────────────────────────────────
# Muvaffaqiyatli bron sahifasi
# ──────────────────────────────────────────────
@login_required
def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking_success.html', {'booking': booking})


# ──────────────────────────────────────────────
# Mening bronlarim
# ──────────────────────────────────────────────
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related(
        'ticket_type__event'
    ).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})


# ──────────────────────────────────────────────
# PDF Ticket yuklab olish
# ──────────────────────────────────────────────
@login_required
def download_ticket(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    event   = booking.event

    # QR code yaratish
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(f"BOOKING:{booking.booking_code}")
    qr.make(fit=True)
    qr_img   = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # PDF buffer
    buffer   = io.BytesIO()
    doc      = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # Ranglar
    DARK   = colors.HexColor('#1e3a5f')
    BLUE   = colors.HexColor('#2563eb')
    LIGHT  = colors.HexColor('#eff6ff')
    GRAY   = colors.HexColor('#64748b')
    WHITE  = colors.white
    BLACK  = colors.black

    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        'TicketSub',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#93c5fd'),
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRAY,
        spaceAfter=2,
    )
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=12,
        textColor=BLACK,
        fontName='Helvetica-Bold',
        spaceAfter=0,
    )
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontSize=20,
        textColor=DARK,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=0,
    )

    # ── Header banner ──
    header_data = [[Paragraph('BiletShop', title_style)],
                   [Paragraph('Elektron bilet / E-Ticket', sub_style)]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), DARK),
        ('TOPPADDING',  (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING',(0,-1),(-1,-1), 16),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Event nomi ──
    story.append(Paragraph(event.title, ParagraphStyle(
        'EventTitle', parent=styles['Normal'],
        fontSize=18, fontName='Helvetica-Bold', textColor=DARK,
        alignment=TA_CENTER, spaceAfter=4,
    )))
    story.append(Paragraph(f"{event.category.name}", ParagraphStyle(
        'CatLabel', parent=styles['Normal'],
        fontSize=10, textColor=BLUE, alignment=TA_CENTER, spaceAfter=12,
    )))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 0.4*cm))

    # ── Asosiy info + QR ──
    info_rows = [
        [Paragraph('Sana va vaqt', label_style),
         Paragraph(event.event_date.strftime('%d.%m.%Y %H:%M'), value_style)],
        [Paragraph('Joy (Venue)', label_style),
         Paragraph(event.venue, value_style)],
        [Paragraph('Shahar', label_style),
         Paragraph(event.city, value_style)],
        [Paragraph('Bilet turi', label_style),
         Paragraph(booking.ticket_type.name, value_style)],
        [Paragraph('Miqdor', label_style),
         Paragraph(str(booking.quantity), value_style)],
        [Paragraph('Jami narx', label_style),
         Paragraph(f"{booking.total_price} so'm", ParagraphStyle(
             'PriceVal', parent=styles['Normal'],
             fontSize=13, fontName='Helvetica-Bold', textColor=BLUE,
         ))],
        [Paragraph('Egasi', label_style),
         Paragraph(f"{booking.user.get_full_name() or booking.user.username}", value_style)],
        [Paragraph('Telefon', label_style),
         Paragraph(booking.phone, value_style)],
    ]

    info_table = Table(info_rows, colWidths=[5*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',  (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0),(-1,-1), 5),
        ('LINEBELOW',   (0, 0), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
    ]))

    qr_image = Image(qr_buffer, width=4.5*cm, height=4.5*cm)

    main_table = Table(
        [[info_table, qr_image]],
        colWidths=[13*cm, 5*cm],
    )
    main_table.setStyle(TableStyle([
        ('VALIGN',  (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',   (1, 0), (1, 0), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
    ]))
    story.append(main_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Bron kodi ──
    story.append(HRFlowable(width='100%', thickness=1.5, lineCap='round',
                             color=BLUE, spaceAfter=0.3*cm))
    story.append(Paragraph('BRON KODI / BOOKING CODE', label_style))
    story.append(Paragraph(booking.booking_code, code_style))
    story.append(HRFlowable(width='100%', thickness=1.5, lineCap='round',
                             color=BLUE, spaceBefore=0.3*cm))
    story.append(Spacer(1, 0.4*cm))

    # ── Footer ──
    story.append(Paragraph(
        'Ushbu elektron bilet tadbir kirish joyida QR kod orqali tasdiqlanadi. '
        'Biletni boshqa shaxsga bermang.',
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=9, textColor=GRAY, alignment=TA_CENTER),
    ))

    doc.build(story)
    buffer.seek(0)

    filename = f"ticket_{booking.booking_code}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ──────────────────────────────────────────────
# Profil
# ──────────────────────────────────────────────
@login_required
def profile_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related(
        'ticket_type__event'
    ).order_by('-created_at')
    return render(request, 'profile.html', {'bookings': bookings})


@login_required
def profile_update(request):
    profile, _ = Profil.objects.get_or_create(user=request.user)
    u_form     = UserUpdateForm(instance=request.user)
    p_form     = ProfileUpdateForm(instance=profile)
    pass_form  = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_user' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, "Ma'lumotlar yangilandi.")
                return redirect('profile')

        elif 'update_avatar' in request.POST:
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, "Avatar yangilandi.")
                return redirect('profile')

        elif 'update_password' in request.POST:
            pass_form = PasswordChangeForm(request.user, request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Parol o'zgartirildi.")
                return redirect('profile')

    return render(request, 'profile_update.html', {
        'u_form': u_form,
        'p_form': p_form,
        'pass_form': pass_form,
    })


# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
