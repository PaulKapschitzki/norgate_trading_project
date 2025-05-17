import norgatedata

# Alle Watchlists abrufen
watchlists = norgatedata.watchlists()

# Struktur der Watchlists ausgeben
print("Typ der watchlists Variable:", type(watchlists))
print("\nErste Watchlist:", watchlists[0] if watchlists else "Keine Watchlists gefunden")
print("\nAlle Watchlists:")
for watchlist in watchlists:
    print(f"- {watchlist}")
