# debug_file.py
import sys

try:
    with open('backend/analyze_and_publish.py', 'rb') as f:
        first_line = f.readline()
        print(f"Première ligne (bytes): {first_line}")
        print(f"Premier caractère (decimal): {first_line[0] if first_line else 'empty'}")
        
        # Essayer d'exécuter juste la première ligne
        try:
            exec(first_line)
        except Exception as e:
            print(f"Erreur sur première ligne: {e}")
            
except Exception as e:
    print(f"Erreur ouverture fichier: {e}")
