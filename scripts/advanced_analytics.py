# ============================================
# ONLINE RETAIL ADVANCED ANALYTICS
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("="*60)
print("ONLINE RETAIL DATA ANALYSIS - BOSHLANDI")
print("="*60)

# ============================================
# 1. MA'LUMOTLARNI YUKLASH
# ============================================

print("\n📂 Ma'lumotlar yuklanmoqda...")

try:
    # Fayllarni o'qish - encoding bilan
    df = pd.read_csv('../data/online_retail_clean.csv', encoding='latin1')
    rfm = pd.read_csv('../data/rfm_analysis.csv', encoding='latin1')
    monthly = pd.read_csv('../data/monthly_revenue.csv', encoding='latin1')
    
    # Ustun nomlarini kichik harfga o'zgartirish
    df.columns = df.columns.str.lower()
    rfm.columns = rfm.columns.str.lower()
    monthly.columns = monthly.columns.str.lower()
    
    # Sana ustunini to'g'rilash
    df['invoicedate'] = pd.to_datetime(df['invoicedate'])
    
    # total_price ustunini yaratish (agar yo'q bo'lsa)
    if 'total_price' not in df.columns:
        df['total_price'] = df['quantity'] * df['unitprice']
    
    print(f"✅ Ma'lumotlar yuklandi!")
    print(f"   - Asosiy ma'lumotlar: {len(df):,} qator")
    print(f"   - RFM tahlil: {len(rfm):,} mijoz")
    print(f"   - Oylik ma'lumotlar: {len(monthly):,} oy")
except Exception as e:
    print(f"❌ XATO: {e}")
    print("CSV fayllar 'data/' papkasida ekanligini tekshiring!")
    exit()

# ============================================
# 2. ASOSIY STATISTIKA
# ============================================

print("\n" + "="*60)
print("📊 ASOSIY METRIKALAR")
print("="*60)

total_revenue = df['total_price'].sum()
total_orders = df['invoiceno'].nunique()
total_customers = df['customerid'].nunique()
total_products = df['stockcode'].nunique()
avg_order_value = total_revenue / total_orders

print(f"\n💰 Jami Daromad:           ${total_revenue:,.2f}")
print(f"🛒 Jami Buyurtmalar:       {total_orders:,}")
print(f"👥 Jami Mijozlar:          {total_customers:,}")
print(f"📦 Jami Mahsulotlar:       {total_products:,}")
print(f"📊 O'rtacha Buyurtma:      ${avg_order_value:,.2f}")

# ============================================
# 3. KUNLIK DAROMAD TENDENTSIYASI
# ============================================

print("\n📈 Kunlik daromad grafigi yaratilmoqda...")

daily_revenue = df.groupby(df['invoicedate'].dt.date)['total_price'].sum().reset_index()
daily_revenue.columns = ['date', 'revenue']

fig = px.line(daily_revenue, x='date', y='revenue', 
              title='<b>Kunlik Daromad Tendentsiyasi</b>',
              labels={'date': 'Sana', 'revenue': 'Daromad ($)'},
              template='plotly_white')

fig.update_traces(line_color='#3498db', line_width=2)
fig.update_layout(
    hovermode='x unified',
    font=dict(size=12),
    title_font_size=16,
    height=500
)

fig.write_html('../visualizations/01_daily_revenue.html')
print("   ✅ Saqlandi: visualizations/01_daily_revenue.html")

# ============================================
# 4. HAFTA KUNI TAHLILI
# ============================================

print("\n📅 Hafta kunlari tahlili...")

df['day_of_week'] = df['invoicedate'].dt.day_name()

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_revenue = df.groupby('day_of_week')['total_price'].sum().reindex(day_order)

plt.figure(figsize=(12, 6))
bars = plt.bar(range(len(weekly_revenue)), weekly_revenue.values, 
               color='#2ecc71', edgecolor='black', linewidth=1.5)

# Eng yuqori kunni ajratib ko'rsatish
max_idx = weekly_revenue.values.argmax()
bars[max_idx].set_color('#e74c3c')

plt.title('Hafta Kunlari bo\'yicha Daromad', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Kun', fontsize=12, fontweight='bold')
plt.ylabel('Daromad ($)', fontsize=12, fontweight='bold')
plt.xticks(range(len(day_order)), day_order, rotation=45)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('../visualizations/02_weekly_revenue.png', dpi=300, bbox_inches='tight')
plt.close()

print("   ✅ Saqlandi: visualizations/02_weekly_revenue.png")
print(f"   📌 Eng yuqori savdo kuni: {weekly_revenue.idxmax()} (${weekly_revenue.max():,.2f})")

# ============================================
# 5. RFM SEGMENTLAR
# ============================================

print("\n👥 RFM segmentlar tahlili...")

segment_counts = rfm['customer_segment'].value_counts()

colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

fig = go.Figure(data=[go.Pie(
    labels=segment_counts.index,
    values=segment_counts.values,
    hole=0.4,
    marker=dict(colors=colors),
    textinfo='label+percent',
    textfont_size=12
)])

fig.update_layout(
    title='<b>Mijozlar Segmentatsiyasi (RFM)</b>',
    annotations=[dict(text='RFM', x=0.5, y=0.5, font_size=24, showarrow=False)],
    height=500,
    showlegend=True
)

fig.write_html('../visualizations/03_rfm_segments.html')
print("   ✅ Saqlandi: visualizations/03_rfm_segments.html")

print("\n   📊 Segmentlar taqsimoti:")
for segment, count in segment_counts.items():
    print(f"      - {segment}: {count:,} ({count/len(rfm)*100:.1f}%)")

# ============================================
# 6. RFM SCATTER PLOT
# ============================================

print("\n🎯 RFM scatter plot...")

# Tekshirish: kerakli ustunlar bormi?
required_cols = ['frequency', 'monetary', 'customer_segment', 'recency', 'customerid']
missing_cols = [col for col in required_cols if col not in rfm.columns]

if missing_cols:
    print(f"   ⚠️  O'tkazib yuborildi: {', '.join(missing_cols)} ustunlari topilmadi")
    print(f"   📋 Mavjud ustunlar: {rfm.columns.tolist()}")
else:
    fig = px.scatter(rfm, x='frequency', y='monetary', 
                     color='customer_segment', size='recency',
                     hover_data=['customerid'],
                     title='<b>RFM Tahlil: Frequency vs Monetary</b>',
                     labels={'frequency': 'Xaridlar Soni', 'monetary': 'Jami Sarflagan ($)'},
                     template='plotly_white',
                     color_discrete_sequence=colors)

    fig.update_layout(height=600, font=dict(size=12))
    fig.write_html('../visualizations/04_rfm_scatter.html')
    print("   ✅ Saqlandi: visualizations/04_rfm_scatter.html")

# ============================================
# 7. TOP MAMLAKATLAR
# ============================================

print("\n🌍 Top mamlakatlar tahlili...")

country_revenue = df.groupby('country').agg({
    'total_price': 'sum',
    'invoiceno': 'nunique',
    'customerid': 'nunique'
}).round(2)

country_revenue.columns = ['revenue', 'orders', 'customers']
country_revenue = country_revenue.sort_values('revenue', ascending=False).head(10)

fig = go.Figure(data=[
    go.Bar(
        y=country_revenue.index,
        x=country_revenue['revenue'],
        orientation='h',
        marker=dict(
            color=country_revenue['revenue'],
            colorscale='Viridis',
            showscale=True
        ),
        text=[f"${x:,.0f}" for x in country_revenue['revenue']],
        textposition='outside'
    )
])

fig.update_layout(
    title='<b>Top 10 Mamlakatlar (Daromad)</b>',
    xaxis_title='Daromad ($)',
    yaxis_title='Mamlakat',
    height=500,
    template='plotly_white'
)

fig.write_html('../visualizations/05_top_countries.html')
print("   ✅ Saqlandi: visualizations/05_top_countries.html")

# ============================================
# 8. OYLIK TREND
# ============================================

print("\n📆 Oylik trend tahlili...")

# Tekshirish: kerakli ustunlar bormi?
if 'month' in monthly.columns and 'revenue' in monthly.columns:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly['month'],
        y=monthly['revenue'],
        mode='lines+markers',
        name='Daromad',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='<b>Oylik Daromad Tendentsiyasi</b>',
        xaxis_title='Oy',
        yaxis_title='Daromad ($)',
        template='plotly_white',
        hovermode='x unified',
        height=500
    )

    fig.write_html('../visualizations/06_monthly_trend.html')
    print("   ✅ Saqlandi: visualizations/06_monthly_trend.html")
else:
    print(f"   ⚠️  O'tkazib yuborildi: kerakli ustunlar topilmadi")
    print(f"   📋 Mavjud ustunlar: {monthly.columns.tolist()}")

# ============================================
# 9. YAKUNIY HISOBOT
# ============================================

print("\n" + "="*60)
print("📋 YAKUNIY HISOBOT")
print("="*60)

report = f"""

{'='*60}
ONLINE RETAIL DATA ANALYSIS - YAKUNIY HISOBOT
{'='*60}

📊 ASOSIY METRIKALAR:
------------------------------------------------------------
💰 Jami Daromad:              ${total_revenue:,.2f}
🛒 Jami Buyurtmalar:          {total_orders:,}
👥 Jami Mijozlar:             {total_customers:,}
📦 Jami Mahsulotlar:          {total_products:,}
📊 O'rtacha Buyurtma Qiymati: ${avg_order_value:,.2f}

👥 RFM SEGMENTATSIYA:
------------------------------------------------------------
{segment_counts.to_string()}

🌍 TOP 5 MAMLAKATLAR (Daromad):
------------------------------------------------------------
{country_revenue['revenue'].head().to_string()}

📈 ENG YUQORI SAVDO KUNI:
------------------------------------------------------------
{weekly_revenue.idxmax()} - ${weekly_revenue.max():,.2f}

✅ YARATILGAN VIZUALIZATSIYALAR:
------------------------------------------------------------
1. Kunlik daromad tendentsiyasi
2. Haftalik daromad tahlili
3. RFM segmentlar (donut chart)
4. RFM scatter plot
5. Top 10 mamlakatlar
6. Oylik daromad trendi

📁 Barcha fayllar 'visualizations/' papkasida saqlandi!

{'='*60}
TAHLIL YAKUNLANDI! ✅
{'='*60}

"""

print(report)

# Hisobotni saqlash
with open('../ANALYSIS_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n💾 Hisobot saqlandi: ANALYSIS_REPORT.txt")
print("\n🎉 Tahlil muvaffaqiyatli yakunlandi!")