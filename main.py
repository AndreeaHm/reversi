import time


class ReversiGame:
    def __init__(self):
        # Inițializăm variabilele pentru algoritm, dificultate, simbolul jucătorului și simbolul adversarului.
        # Inițializăm tabla de joc apelând metoda initialize_board, setând tabla la configurația inițială.
        # Setăm jucătorul curent la 'X', presupunând că jucătorul 'X' începe jocul.
        self.algorithm = None
        self.difficulty = None
        self.player_symbol = None
        self.opponent_symbol = None
        self.board = self.initialize_board()
        self.current_player = 'X'

    @staticmethod
    def initialize_board():
        # Creează o tablă de 8x8 cu toate celulele inițializate cu spații.
        # Plasăm patru piese în centrul tablei în forma standard a jocului Reversi.
        board = [[' ' for _ in range(8)] for _ in range(8)]
        board[3][3], board[4][4] = 'X', 'X'
        board[3][4], board[4][3] = 'O', 'O'
        return board

    def display_board(self):
        # Afișăm tabla de joc curentă în consolă cu etichete pentru rânduri și coloane.
        print("   " + "   ".join(map(str, range(1, 9))))  # Adaugam etichete pentru coloane
        print("  +" + "---+" * 8)
        for y, row in enumerate(self.board, start=1):
            print(f"{y} | " + " | ".join(row) + " |")  # Adaugam etichete pentru rânduri
            print("  +" + "---+" * 8)

    @staticmethod
    def validate_input(prompt, valid_options):
        # Solicită și validează intrarea utilizatorului, asigurându-se că este una din opțiunile valide.
        while True:
            choice = input(prompt).strip()
            if choice in valid_options:
                return choice
            else:
                print("Opțiune invalidă, încearcă din nou.")

    def choose_options(self):
        # Permite utilizatorului să aleagă algoritmul, dificultatea și simbolul cu care dorește să joace.
        # În acest proiect este implementat doar algoritmul Min-Max.
        algorithm_choice = self.validate_input(
            "Alege algoritmul (1: A*, 2: Min-Max, 3: Rețele Bayesiene):",
            ['1', '2', '3'])
        self.algorithm = ['A*', 'Min-Max', 'Rețele Bayesiene'][int(algorithm_choice) - 1]

        self.difficulty = int(self.validate_input(
            "Alege dificultatea (1-5, unde 5 este cea mai dificilă):",
            ['1', '2', '3', '4', '5']))

        self.player_symbol = self.validate_input(
            "Cu ce simbol dorești să joci? (X pentru MAX, O pentru MIN):",
            ['X', 'O'])
        self.opponent_symbol = 'O' if self.player_symbol == 'X' else 'X'

    def get_valid_moves(self, player_symbol):
        # Definim direcțiile de verificare pentru mutările valide: 8 direcții posibile.
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        valid_moves = []  # Lista pentru stocarea mutărilor valide găsite.

        # Iterează peste toate celulele tablei de joc.
        for y in range(8):
            for x in range(8):
                # Dacă celula curentă nu este goală, sărim la următoarea iterație.
                if self.board[y][x] != ' ':
                    continue
                # Pentru fiecare direcție posibilă, verificăm dacă plasarea unei piese aici ar fi validă.
                for dx, dy in directions:
                    # Calculăm coordonatele primei celule în direcția (dx, dy).
                    nx, ny = x + dx, y + dy
                    # Verificăm dacă direcția curentă este validă pentru capturarea pieselor adversarului.
                    if self.is_valid_direction(player_symbol, nx, ny, dx, dy):
                        # Dacă se găsește cel puțin o direcție validă, adaugăm această mutare în lista de mutări valide.
                        valid_moves.append((x, y))
                        # Oprim căutarea altor direcții, deoarece o singură direcție validă este suficientă.
                        break

        return valid_moves

    def is_valid_direction(self, player_symbol, x, y, dx, dy):
        # Identificăm simbolul adversarului în funcție de simbolul jucătorului curent.
        opponent_symbol = 'O' if player_symbol == 'X' else 'X'
        found_opponent = False

        # Verificăm consecutiv celulele din direcția specificată (dx, dy) începând de la coordonatele (x, y).
        while 0 <= x < 8 and 0 <= y < 8:
            if self.board[y][x] == opponent_symbol:
                # Dacă întâlnim o piesă a adversarului, setăm flag-ul found_opponent pe True.
                found_opponent = True
            elif self.board[y][x] == player_symbol:
                # Dacă întâlnim o altă piesă a jucătorului curent, înseamnă că secvența este validă pentru capturare
                # doar dacă între aceste două piese au fost găsite una sau mai multe piese ale adversarului.
                return found_opponent
            else:
                # Dacă întâlnim o celulă goală, întrerupem bucla, deoarece nu putem captura peste celule goale.
                break

            # Continuăm la următoarea celulă în direcția specificată.
            x += dx
            y += dy

        # Dacă bucla se termină fără să se întâlnească o a doua piesă a jucătorului, return False (capturare invalidă).
        return False

    def apply_move(self, move, player_symbol):
        # Definițiile direcțiilor în care poate fi aplicată o mutare: cele 8 direcții posibile.
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        x, y = move  # Coordonatele unde jucătorul a decis să plaseze o piesă.
        self.board[y][x] = player_symbol  # Plasează simbolul jucătorului pe tabla de joc.

        # Iterăm prin fiecare direcție pentru a verifica dacă mutarea curentă poate captura piesele adversarului.
        for dx, dy in directions:
            # Începem verificarea din celula adiacentă în direcția (dx, dy).
            nx, ny = x + dx, y + dy
            # Lista pentru stocarea pieselor temporare care pot fi întoarse.
            pieces_to_flip = []
            # Continuăm să ne deplasăm în direcția (dx, dy) până când ieșim din tablă sau întâlnim o condiție de oprire.
            while 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == ('X' if player_symbol == 'O' else 'O'):
                # Adăugăm coordonatele piesei adversarului care poate fi capturată.
                pieces_to_flip.append((nx, ny))
                nx += dx
                ny += dy

            # Verificăm dacă bucla s-a încheiat datorită întâlnirii unei piese a jucătorului curent,
            # nu a unei celule goale sau ieșiri din tablă.
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == player_symbol:
                # Dacă există piese de întors și capătul lanțului este o piesă a jucătorului curent,
                # întoarce piesele adversarului.
                for px, py in pieces_to_flip:
                    self.board[py][px] = player_symbol  # Întoarcem fiecare piesă capturată.

        # Schimbăm jucătorul curent după aplicarea mutării.
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def player_move(self):
        # Obținem lista de mutări valide pentru simbolul jucătorului curent.
        valid_moves = self.get_valid_moves(self.player_symbol)
        if not valid_moves:
            print("Nu mai există mișcări valide.")
            return False

        move = None  # Inițializăm variabila pentru mutarea selectată.

        # Buclă pentru a obține o mutare validă de la jucător.
        while move not in valid_moves:
            try:
                # Solicităm jucătorului să introducă mutarea sub forma 'rând coloană'.
                print(f"Rândul lui {self.current_player}'. Introdu mișcarea (format 'rând col'): ")
                y, x = map(int, input().split())  # Converteste inputul în coordonate întregi.
                move = (x - 1, y - 1)  # Ajustează coordonatele pentru indexarea de la zero a listelor.

                # Verificăm dacă mutarea selectată este în lista de mutări valide.
                if move in valid_moves:
                    self.apply_move(move, self.player_symbol)
                    return True
                else:
                    print("Mișcare invalidă.")
            except ValueError:
                print("Format invalid, folosește 'rând col'.")
        return True

    def find_best_move(self, joc, depth):
        # Această funcție folosește algoritmul Min-Max pentru a determina cea mai bună mutare posibilă pentru calculator.
        _, best_move = self.min_max(joc, depth, True)
        return best_move

    def computer_move(self):
        # Această funcție este responsabilă pentru gestionarea mutării calculatorului.
        # Folosește funcția `find_best_move` pentru a obține cea mai bună mutare bazată pe dificultatea curentă a jocului.
        best_move = self.find_best_move(self, self.difficulty)  # Exemplu: căutăm până la adâncimea 3
        if best_move:
            print(f"Calculatorul alege mutarea: {best_move}")
            self.apply_move(best_move, self.opponent_symbol)
            return True
        else:
            print("Calculatorul nu are mutări valide.")
            return False

    def is_game_over(self):
        # Verificăm dacă jocul s-a terminat verificând două condiții principale:
        # 1. Toate celulele de pe tablă sunt ocupate.
        if all(cell != ' ' for row in self.board for cell in row):
            return True  # Dacă tablă este complet umplută, jocul este considerat terminat.
        # 2. Niciunul dintre jucători nu are mutări valide disponibile.
        if not self.get_valid_moves(self.player_symbol) and not self.get_valid_moves(self.opponent_symbol):
            return True  # Dacă niciun jucător nu poate muta, jocul este de asemenea terminat.
        return False  # Dacă niciuna din condiții nu este îndeplinită, jocul continuă.

    def calculate_scores(self):
        # Calculează și returnează scorurile pentru ambii jucători bazat pe numărul de piese de pe tablă.
        scores = {'X': 0, 'O': 0}
        for row in self.board:
            for cell in row:
                if cell in scores:
                    scores[cell] += 1
        return scores

    @staticmethod
    def determine_winner(scores):
        # Determină câștigătorul jocului bazat pe scorurile jucătorilor.
        if scores['X'] > scores['O']:
            return 'X', scores
        elif scores['O'] > scores['X']:
            return 'O', scores
        else:
            return 'None', scores  # Tie

    def min_max(self, games, depth, maximizing_player):
        # Verificăm dacă s-a ajuns la adâncimea maximă de căutare sau dacă jocul s-a terminat.
        if depth == 0 or games.is_game_over():
            # Calculează și returnează scorul actual al tablei de joc fără a continua recursivitatea.
            return games.calculate_score(), None

        best_move = None  # Inițializează cea mai bună mutare găsită la acest nivel.

        if maximizing_player:
            # Pentru jucătorul care maximizează (MAX), scopul este să obțină cel mai mare scor posibil.
            max_eval = float('-inf')  # Inițializează evaluarea la minus infinit pentru comparație.
            # Explorează toate mutările valide pentru jucătorul curent.
            for move in games.get_valid_moves(games.current_player):
                # Creează o copie a jocului pentru a simula mutarea fără a afecta jocul actual.
                new_game = games.copy_game()
                # Aplică mutarea pe noua instanță a jocului.
                new_game.apply_move(move, games.current_player)
                # Recursiv, calculează evaluarea mutării folosind min_max pentru jucătorul advers (MIN).
                evalu = self.min_max(new_game, depth - 1, False)[0]
                # Actualizează evaluarea maximă și cea mai bună mutare dacă evaluarea curentă este mai mare.
                if evalu > max_eval:
                    max_eval = evalu
                    best_move = move
            # Returnează cea mai bună evaluare și mutare pentru acest nivel
            return max_eval, best_move
        else:
            # Pentru jucătorul care minimizează (MIN), scopul este să minimizeze scorul adversarului.
            min_eval = float('inf')  # Inițializează evaluarea la infinit pentru comparație.
            # Explorează toate mutările valide pentru adversar.
            for move in games.get_valid_moves(games.opponent_symbol):
                new_game = games.copy_game()  # Creează o nouă copie a jocului pentru simulare.
                new_game.apply_move(move, games.opponent_symbol)  # Aplică mutarea.
                # Recursiv, calculează evaluarea mutării folosind min_max pentru jucătorul MAX.
                evalu = self.min_max(new_game, depth - 1, True)[0]
                # Actualizează evaluarea minimă și cea mai bună mutare dacă evaluarea curentă este mai mică.
                if evalu < min_eval:
                    min_eval = evalu
                    best_move = move
            # Returnează cea mai bună evaluare și mutare pentru acest nivel.
            return min_eval, best_move

    def copy_game(self):
        new_game = ReversiGame()
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.opponent_symbol = self.opponent_symbol
        # Copiază alte atribute necesare
        return new_game

    def calculate_score(self):
        # Calculează scorul actual al jocului din perspectiva jucătorului curent.
        # Suma pieselor jucătorului curent de pe tablă.
        player_score = sum(row.count(self.current_player) for row in self.board)
        # Suma pieselor adversarului de pe tablă.
        opponent_score = sum(row.count(self.opponent_symbol) for row in self.board)
        # Scorul este diferența dintre numărul de piese ale jucătorului curent și cele ale adversarului.
        # Un scor pozitiv înseamnă un avantaj pentru jucătorul curent, în timp ce un scor negativ indică un avantaj pentru adversar.
        return player_score - opponent_score

    def play_game(self):
        # Începe măsurarea timpului de joc.
        start_time = time.time()
        # Lasă jucătorul să aleagă opțiunile de joc cum ar fi dificultatea și simbolul cu care joacă.
        self.choose_options()
        game_over = False  # Inițializează starea de terminare a jocului.

        # Ciclul principal al jocului, care continuă până când jocul se termină.
        while not game_over:
            # Afișează informații despre runda curentă și scorurile actuale.
            print(
                f"\nRândul lui {self.current_player}. Scor curent: X - {self.calculate_scores()['X']}, O - {self.calculate_scores()['O']}.")
            self.display_board()  # Afișează starea actuală a tablei de joc.

            # Determină al cui este rândul și execută mutarea corespunzătoare.
            if self.current_player == self.player_symbol:
                # Dacă este rândul jucătorului uman:
                if not self.player_move():  # Încercă să facă o mutare.
                    print("Nicio mutare validă disponibilă. Schimbăm jucătorul.")
                self.current_player = self.opponent_symbol  # Schimbă jucătorul.
            else:
                # Dacă este rândul calculatorului:
                if not self.computer_move():  # Încercă să facă o mutare.
                    print("Calculatorul nu are mutări valide. Schimbăm jucătorul.")
                self.current_player = self.player_symbol  # Schimbă jucătorul.

            # Verifică dacă jocul s-a terminat.
            if self.is_game_over():
                scores = self.calculate_scores()  # Calculează scorurile finale.
                winner, scores = self.determine_winner(scores)  # Determină câștigătorul.
                self.display_board()  # Afișează tabla finală.
                print(f"Jocul s-a încheiat. Scor final: X = {scores['X']}, O = {scores['O']}.")
                if winner != 'None':  # Dacă există un câștigător.
                    print(f"Câștigătorul este: {winner}!")
                else:  # Dacă jocul se termină la egalitate.
                    print("Jocul s-a terminat la egalitate!")
                break  # Ieșire din bucla de joc.

        # Calculează și afișează durata totală a jocului.
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Jocul s-a încheiat în {total_time:.2f} secunde.")


if __name__ == "__main__":
    game = ReversiGame()
    game.play_game()
