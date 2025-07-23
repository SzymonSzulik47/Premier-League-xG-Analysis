import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr 
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
# Wczytanie danych
df = pd.read_csv("premier-League-24.csv")

# Kasujemy wiersze, gdzie brakuje wyniku meczu
df = df.dropna(subset=['Score'])

# Rozdzielenie kolumny 'Score' na gole gospodarzy i gości
df[['home_goals', 'away_goals']] = df['Score'].str.split('–', expand=True).astype(int)

# Zmiana nazw kolumn dla jasności
df.rename(columns={
    'Home': 'home_team',
    'Away': 'away_team',
    'xG': 'home_xG',
    'xG.1': 'away_xG'
}, inplace=True)

# Przygotowanie danych meczowych
home = df[['home_team', 'home_goals', 'home_xG', 'away_goals', 'away_xG']].copy()
home.columns = ['team', 'goals_for', 'xG_for', 'goals_against', 'xGA']

away = df[['away_team', 'away_goals', 'away_xG', 'home_goals', 'home_xG']].copy()
away.columns = ['team', 'goals_for', 'xG_for', 'goals_against', 'xGA']

# Połączenie meczów domowych i wyjazdowych
all_matches = pd.concat([home, away])

# Agregacja na poziomie zespołów
team_stats = all_matches.groupby('team').sum().reset_index()
team_stats['xG_diff'] = team_stats['xG_for'] - team_stats['goals_for']
team_stats['xGA_diff'] = team_stats['xGA'] - team_stats['goals_against']

# Sortowanie po różnicy xG
team_stats = team_stats.sort_values(by='xG_diff', ascending=False)

# Wyświetlenie statystyk
print(team_stats)
plt.figure(figsize=(10,6))
sns.scatterplot(data=team_stats, x='xG_for', y='goals_for', hue='team')
plt.title('xG vs. Bramki zdobyte (2023/24)')
plt.xlabel('xG')
plt.ylabel('Bramki zdobyte')
plt.plot([team_stats['xG_for'].min(), team_stats['xG_for'].max()],
         [team_stats['xG_for'].min(), team_stats['xG_for'].max()],
         linestyle='--', color='gray')
plt.tight_layout()
plt.show()

#under i overperformerzy
underperformers = team_stats[team_stats['xG_diff'] > 0].sort_values(by='xG_diff', ascending=False)
overperformers = team_stats[team_stats['xG_diff'] < 0].sort_values(by='xG_diff')

# Wyświetlenie tabel
print("🔻 UNDERPERFORMERZY (xG > gole):\n")
print(underperformers[['team', 'xG_for', 'goals_for', 'xG_diff']].to_string(index=False))

print("\n🔺 OVERPERFORMERZY (xG < gole):\n")
print(overperformers[['team', 'xG_for', 'goals_for', 'xG_diff']].to_string(index=False))
# 🔻 Underperformerzy
plt.figure(figsize=(12,6))
sns.barplot(data=underperformers, x='team', y='xG_diff', hue='team', palette='Reds_r', legend=False)
plt.title('Underperformerzy – drużyny, które powinny strzelić więcej (xG > gole)')
plt.ylabel('xG – gole')
plt.xlabel('Drużyna')
plt.xticks(rotation=45)
plt.axhline(0, color='gray', linestyle='--')
plt.tight_layout()
plt.show()

# 🔺 Overperformerzy
plt.figure(figsize=(12,6))
sns.barplot(data=overperformers, x='team', y='xG_diff', hue='team', palette='Greens', legend=False)
plt.title('Overperformerzy – drużyny, które strzeliły ponad stan (xG < gole)')
plt.ylabel('xG – gole')
plt.xlabel('Drużyna')
plt.xticks(rotation=45)
plt.axhline(0, color='gray', linestyle='--')
plt.tight_layout()
plt.show()

# Gotowe dane końcowej tabeli Premier League 2023/24
points_data = {
    'Manchester City': 91,
    'Arsenal': 89,
    'Liverpool': 82,
    'Aston Villa': 68,
    'Tottenham': 66,
    'Chelsea': 63,
    'Newcastle Utd': 60,
    'Manchester Utd': 60,
    'West Ham': 52,
    'Crystal Palace': 49,
    'Brighton': 48,
    'Bournemouth': 48,
    'Fulham': 47,
    'Wolves': 46,
    'Everton': 40,
    'Brentford': 39,
    "Nott'ham Forest": 32,
    'Luton Town': 26,
    'Burnley': 24,
    'Sheffield Utd': 16
}
# Przypisz punkty z gotowego słownika
team_stats['points'] = team_stats['team'].map(points_data)
team_stats['position'] = team_stats['points'].rank(ascending=False, method='min').astype(int)
print(team_stats[team_stats['points'].isna()])
team_stats = team_stats.sort_values(by='position')

#Analiza "czy xG tłumaczy liczbę punktów"

print("\n--- Analiza: Czy xG tłumaczy liczbę punktów? ---\n")

#1. Korelacja między xG_for a punktami
correlation_xg_points, _ = pearsonr(team_stats['xG_for'], team_stats['points'])
print(f"Współczynnik korelacji Pearsona między xG_for (xG zdobyte) a punktami: {correlation_xg_points:.3f}")

#Korelacja między xGA a punktami
correlation_xga_points, _ = pearsonr(team_stats['xGA'], team_stats['points'])
print(f"Współczynnik korelacji Pearsona między xGA (xG stracone) a punktami: {correlation_xga_points:.3f}")

#Korelacja między xG_diff a punktami
correlation_xg_diff_points, _ = pearsonr(team_stats['xG_diff'], team_stats['points'])
print(f"Współczynnik korelacji Pearsona między xG_diff (xG zdobyte - gole zdobyte) a punktami: {correlation_xg_diff_points:.3f}")

#Korelacja między xGA_diff a punktami
correlation_xga_diff_points, _ = pearsonr(team_stats['xGA_diff'], team_stats['points'])
print(f"Współczynnik korelacji Pearsona między xGA_diff (xGA - gole stracone) a punktami: {correlation_xga_diff_points:.3f}")

#Wizualizacja korelacji (Scatter plot)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=team_stats, x='xG_for', y='points', hue='team', s=100)
for i, row in team_stats.iterrows():
    plt.text(row['xG_for'] + 1, row['points'], row['team'], fontsize=9)
plt.title('Punkty vs. xG zdobyte (2023/24)')
plt.xlabel('xG zdobyte')
plt.ylabel('Punkty')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=team_stats, x='xGA', y='points', hue='team', s=100)
for i, row in team_stats.iterrows():
    plt.text(row['xGA'] + 1, row['points'], row['team'], fontsize=9)
plt.title('Punkty vs. xG stracone (2023/24)')
plt.xlabel('xG stracone')
plt.ylabel('Punkty')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
#Regresja Liniowa
#Przygotowanie danych dla regresji
#Możemy spróbować przewidywać punkty na podstawie xG_for, xGA lub ich różnicy
X = team_stats[['xG_for', 'xGA']] # Zmienne niezależne
y = team_stats['points']          # Zmienna zależna

# Podział danych na zbiór treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Tworzenie i trenowanie modelu regresji liniowej
model = LinearRegression()
model.fit(X_train, y_train)

# Przewidywanie na zbiorze testowym
y_pred = model.predict(X_test)

#Ocena modelu
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Regresji Liniowej (zmienne: xG_for, xGA):")
print(f"Współczynnik R-kwadrat (R²): {r2:.3f}")
print(f"Błąd średniokwadratowy (MSE): {mse:.2f}")
print(f"Współczynniki modelu: {model.coef_}")
print(f"Przechwycenie (intercept): {model.intercept_:.2f}")
# Interpretacja współczynników
print(f"\nInterpretacja współczynników regresji:")
print(f"  Dla xG_for: {model.coef_[0]:.2f} - Wzrost o 1 xG_for przewidywalnie zwiększa punkty o tę wartość.")
print(f"  Dla xGA: {model.coef_[1]:.2f} - Wzrost o 1 xGA przewidywalnie zmienia punkty o tę wartość.")
#Wizualizacja regresji (dla jednej zmiennej dla uproszczenia)
#Możemy zwizualizować regresję dla xG_for vs. punkty
plt.figure(figsize=(10, 6))
sns.regplot(data=team_stats, x='xG_for', y='points', scatter_kws={'s': 100}, line_kws={'color': 'red'})
for i, row in team_stats.iterrows():
    plt.text(row['xG_for'] + 1, row['points'], row['team'], fontsize=9)
plt.title('Regresja Liniowa: Punkty vs. xG zdobyte')
plt.xlabel('xG zdobyte')
plt.ylabel('Punkty')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

#Wizualizacja regresji dla xGA vs. punkty
plt.figure(figsize=(10, 6))
sns.regplot(data=team_stats, x='xGA', y='points', scatter_kws={'s': 100}, line_kws={'color': 'red'})
for i, row in team_stats.iterrows():
    plt.text(row['xGA'] + 1, row['points'], row['team'], fontsize=9)
plt.title('Regresja Liniowa: Punkty vs. xG stracone')
plt.xlabel('xG stracone')
plt.ylabel('Punkty')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
#Analiza reszt
#Reszty to różnica między rzeczywistymi a przewidywanymi wartościami. Ich analiza może pomóc w ocenie, czy model jest odpowiedni.
#Dla uproszczenia, obliczmy reszty dla całego zbioru danych (jeśli nie dzieliliśmy na treningowy/testowy)
#lub dla zbioru testowego, jeśli to zrobiliśmy
#Tutaj obliczymy reszty dla całego zbioru, aby zobaczyć je dla wszystkich drużyn
team_stats['predicted_points'] = model.predict(team_stats[['xG_for', 'xGA']])
team_stats['residuals'] = team_stats['points'] - team_stats['predicted_points']
plt.figure(figsize=(10, 6))
sns.barplot(data=team_stats.sort_values(by='residuals', ascending=False), x='team', y='residuals', hue='team', palette='viridis', legend=False)
plt.axhline(0, color='gray', linestyle='--')
plt.title('Reszty modelu regresji liniowej (Rzeczywiste Punkty - Przewidywane Punkty)')
plt.xlabel('Drużyna')
plt.ylabel('Reszty')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

print("\n--- Analiza Reszt ---")
print("Dodatnie reszty oznaczają, że drużyna zdobyła więcej punktów niż przewidywał model na podstawie xG. ")
print("Ujemne reszty oznaczają, że drużyna zdobyła mniej punktów niż przewidywał model na podstawie xG.")
print(team_stats[['team', 'points', 'predicted_points', 'residuals']].sort_values(by='residuals', ascending=False).to_string(index=False))

