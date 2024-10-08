import sqlite3 

from flask import Flask, flash, request, render_template, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import subprocess
import json
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fide_player.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable modification tracking, improve performance

app.secret_key = 'your_secret_key_here'

db = SQLAlchemy(app)

class ChessPlayers(db.Model):
    FideID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100), nullable=False)
    Federation = db.Column(db.String(100), nullable=True)
    Sex = db.Column(db.String(1), nullable=True)
    YearOfBirth = db.Column(db.Integer, nullable=True)
    FIDETitle = db.Column(db.String(10), nullable=True)
    RatingStandard = db.Column(db.Integer, nullable=True)
    RatingRapid = db.Column(db.Integer, nullable=True)
    RatingBlitz = db.Column(db.Integer, nullable=True)

    # Additional fields
    ACFID = db.Column(db.String(100), nullable=True)

    RatingACFStandard = db.Column(db.String(100), nullable=True)
    RatingACFQuick  = db.Column(db.String(100), nullable=True)

    ChessTempo = db.Column(db.String(100), nullable=True)
    ChessBase = db.Column(db.String(100), nullable=True)
    ChessCom = db.Column(db.String(100), nullable=True)
    LiChess = db.Column(db.String(100), nullable=True)
    Chess365 = db.Column(db.String(100), nullable=True)
    ChessGames = db.Column(db.String(100), nullable=True)
    ChessResults = db.Column(db.String(100), nullable=True)    

    def __init__(self, FideID, FullName, Federation=None, Sex=None, YearOfBirth=None, FIDETitle=None, 
                 RatingStandard=None, RatingRapid=None, RatingBlitz=None, 
                 ACFID=None, RatingACFStandard=None, RatingACFQuick = None, 
                 ChessTempo=None, ChessBase=None, ChessCom=None, LiChess=None, Chess365=None, ChessGames=None, ChessResults=None):
        
        self.FideID = FideID
        self.FullName = FullName
        self.Federation = Federation
        self.Sex = Sex
        self.YearOfBirth = YearOfBirth
        self.FIDETitle = FIDETitle
        self.RatingStandard = RatingStandard
        self.RatingRapid = RatingRapid
        self.RatingBlitz = RatingBlitz

        # Additional fields
        self.ACFID = ACFID
        self.RatingACFStandard = RatingACFStandard
        self.RatingACFQuick = RatingACFQuick
        self.ChessTempo = ChessTempo
        self.ChessBase = ChessBase
        self.ChessCom = ChessCom
        self.LiChess = LiChess
        self.Chess365 = Chess365
        self.ChessGames = ChessGames
        self.ChessResults = ChessResults

    def __repr__(self):
        return f"FidePlayer(FideID={self.FideID}, FullName={self.FullName}, Federation={self.Federation}, " \
               f"Sex={self.Sex}, YearOfBirth={self.YearOfBirth}, FIDETitle={self.FIDETitle}, " \
               f"RatingStandard={self.RatingStandard}, RatingRapid={self.RatingRapid}, RatingBlitz={self.RatingBlitz}, " \
               f"ACFID={self.ACFID}, RatingACFStandard={self.RatingACFStandard}, RatingACFQuick={self.RatingACFQuick}, " \
               f"ChessTempo={self.ChessTempo}, ChessBase={self.ChessBase}, ChessCom={self.ChessCom}, " \
               f"LiChess={self.LiChess}, Chess365={self.Chess365}, ChessGames={self.ChessGames}, " \
               f"ChessResults={self.ChessResults})"

@app.route('/')    
def home():
    return render_template('home.html')

@app.route('/add_chess_player', methods=['GET', 'POST'])
def add_chess_player():
    if request.method == 'POST':
        if not request.form['FideID'] or not request.form['FullName']:
            flash('Please enter all the required fields', 'error')
        else:
            try:
                FideID = int(request.form['FideID'])
            except ValueError:
                flash('FideID must be an integer', 'error')
                return redirect(url_for('add_chess_player'))

            fide_player = ChessPlayers(
                FideID=FideID,
                FullName=request.form['FullName'],
                Federation=request.form.get('Federation') or None,
                Sex=request.form.get('Sex') or None,
                YearOfBirth=int(request.form['YearOfBirth']) if request.form.get('YearOfBirth') else None,
                FIDETitle=request.form.get('FIDETitle') or None,
                RatingStandard=int(request.form['RatingStandard']) if request.form.get('RatingStandard') else None,
                RatingRapid=int(request.form['RatingRapid']) if request.form.get('RatingRapid') else None,
                RatingBlitz=int(request.form['RatingBlitz']) if request.form.get('RatingBlitz') else None,
                
                ACFID=request.form.get('ACFID') or None,
                RatingACFStandard=request.form.get('RatingACFStandard') or None,
                RatingACFQuick=request.form.get('RatingACFQuick') or None,
                ChessTempo=request.form.get('ChessTempo') or None,
                ChessBase=request.form.get('ChessBase') or None,
                ChessCom=request.form.get('ChessCom') or None,
                LiChess=request.form.get('LiChess') or None,
                Chess365=request.form.get('Chess365') or None,
                ChessGames=request.form.get('ChessGames') or None,
                ChessResults=request.form.get('ChessResults') or None
            )
            existing_player = ChessPlayers.query.filter(
                (ChessPlayers.FideID == FideID) | (ChessPlayers.FullName == request.form['FullName'])
            ).first()

            if existing_player:
                flash('A player with the same FideID or FullName already exists', 'error')
            else:
                db.session.add(fide_player)
                db.session.commit()
                flash('Record was successfully added')
                return redirect(url_for('list_players'))

            flash('Record was successfully added')
            return redirect(url_for('list_players'))

    return render_template('add_chess_player.html')

@app.route('/list_players_by_rating')
def list_players_by_rating():

    players = ChessPlayers.query.all()

    print("All players in'list_players_by_rating':")
    for player in players:
        print(f"FideID: {player.FideID}, FullName: {player.FullName}, Federation: {player.Federation}, Sex: {player.Sex}, YearOfBirth: {player.YearOfBirth}, FIDETitle: {player.FIDETitle}, RatingStandard: {player.RatingStandard}, RatingRapid: {player.RatingRapid}, RatingBlitz: {player.RatingBlitz}")
                                                                                   
    return render_template('list_players_by_rating.html', players=players)
    
@app.route('/list_players')
def list_players():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'FideID')
    order = request.args.get('order', 'asc')

    if sort_by == 'name':
        if order == 'asc':
            players = ChessPlayers.query.order_by(ChessPlayers.FullName.asc()).paginate(page=page, per_page=100)
        else:
            players = ChessPlayers.query.order_by(ChessPlayers.FullName.desc()).paginate(page=page, per_page=100)
    elif sort_by == 'YoB':
        if order == 'asc':
            players = ChessPlayers.query.order_by(ChessPlayers.YearOfBirth.asc()).paginate(page=page, per_page=100)
        else:
            players = ChessPlayers.query.order_by(ChessPlayers.YearOfBirth.desc()).paginate(page=page, per_page=100)
    elif sort_by == 'RatingStandard':
        if order == 'asc':
            players = ChessPlayers.query.order_by(ChessPlayers.RatingStandard.asc()).paginate(page=page, per_page=100)
        else:
            players = ChessPlayers.query.order_by(ChessPlayers.RatingStandard.desc()).paginate(page=page, per_page=100)
    elif sort_by == 'RatingACFStandard':
        if order == 'asc':
            players = ChessPlayers.query.order_by(ChessPlayers.RatingACFStandard.asc()).paginate(page=page, per_page=100)
        else:
            players = ChessPlayers.query.order_by(ChessPlayers.RatingACFStandard.desc()).paginate(page=page, per_page=100)
    else:
        if order == 'asc':
            players = ChessPlayers.query.order_by(ChessPlayers.FideID.asc()).paginate(page=page, per_page=100)
        else:
            players = ChessPlayers.query.order_by(ChessPlayers.FideID.desc()).paginate(page=page, per_page=100)

    return render_template('list_players.html', players=players, sort_by=sort_by, order=order)

@app.route('/edit_player/<int:FideID>', methods=['GET', 'POST'])
def edit_player(FideID):
    player = ChessPlayers.query.get_or_404(FideID)
    if request.method == 'POST':
        player.FullName = request.form['FullName']
        player.Federation = request.form.get('Federation') or None
        player.Sex = request.form.get('Sex') or None
        player.YearOfBirth = int(request.form['YearOfBirth']) if request.form.get('YearOfBirth') else None
        player.FIDETitle = request.form.get('FIDETitle') or None
        player.RatingStandard = int(request.form['RatingStandard']) if request.form.get('RatingStandard') else None
        player.RatingRapid = int(request.form['RatingRapid']) if request.form.get('RatingRapid') else None
        player.RatingBlitz = int(request.form['RatingBlitz']) if request.form.get('RatingBlitz') else None
        
        player.ACFID = request.form.get('ACFID') or None
        player.RatingACFStandard = request.form.get('RatingACFStandard') or None
        player.RatingACFQuick = request.form.get('RatingACFQuick') or None
        player.ChessTempo = request.form.get('ChessTempo') or None
        player.ChessBase = request.form.get('ChessBase') or None
        player.ChessCom = request.form.get('ChessCom') or None
        player.LiChess = request.form.get('LiChess') or None
        player.Chess365 = request.form.get('Chess365') or None
        player.ChessGames = request.form.get('ChessGames') or None
        player.ChessResults = request.form.get('ChessResults') or None

        db.session.commit()
        return redirect(url_for('list_players'))
    return render_template('edit_player.html', player=player)

@app.route('/delete_player/<int:FideID>', methods=['GET', 'POST'])
def delete_player(FideID):
    player = ChessPlayers.query.get_or_404(FideID)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('list_players'))

@app.route('/scrap-fide-info/<int:FideID>', methods=['GET', 'POST'])    
def scrap_fide_info(FideID):

    # Execute the command line script to scrape the FIDE info
    result = subprocess.run(['fide-ratings-scraper', 'get', 'info', str(FideID)], capture_output=True, text=True)

    # Parse the JSON output
    fide_info = json.loads(result.stdout)

    # Set player's info
    player = ChessPlayers.query.get_or_404(FideID)
    player.FullName = fide_info.get('name')
    player.Federation = fide_info.get('federation')
    player.YearOfBirth = fide_info.get('birth_year')
    player.Sex = fide_info.get('sex')
    player.FIDETitle = fide_info.get('title')
    player.RatingStandard = fide_info.get('standard_elo')
    player.RatingRapid = fide_info.get('rapid_elo')
    player.RatingBlitz = fide_info.get('blitz_elo')

    # print(f"Standard Rating: {player.RatingStandard}, Rapid Rating: {player.RatingRapid}, Blitz Rating: {player.RatingBlitz}")

    db.session.commit()

    return redirect(url_for('edit_player', FideID=FideID))


@app.route('/export_players')
def export_players():
    players = ChessPlayers.query.all()
    filename = f"ChessPlayer-{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = os.path.join('exports', filename)

    os.makedirs('exports', exist_ok=True)

    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [column.name for column in ChessPlayers.__table__.columns]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for player in players:
            writer.writerow({field: getattr(player, field) for field in fieldnames})

    return redirect(url_for('static', filename=f'exports/{filename}'))

@app.route('/import_players', methods=['GET', 'POST'])
def import_players():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)

            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    fide_player = ChessPlayers(
                        FideID=int(row['FideID']),
                        FullName=row['FullName'],
                        Federation=row.get('Federation'),
                        Sex=row.get('Sex'),
                        YearOfBirth=int(row['YearOfBirth']) if row.get('YearOfBirth') else None,
                        FIDETitle=row.get('FIDETitle'),
                        RatingStandard=int(row['RatingStandard']) if row.get('RatingStandard') else None,
                        RatingRapid=int(row['RatingRapid']) if row.get('RatingRapid') else None,
                        RatingBlitz=int(row['RatingBlitz']) if row.get('RatingBlitz') else None,
                        ACFID=row.get('ACFID'),
                        RatingACFStandard=row.get('RatingACFStandard'),
                        RatingACFQuick=row.get('RatingACFQuick'),
                        ChessTempo=row.get('ChessTempo'),
                        ChessBase=row.get('ChessBase'),
                        ChessCom=row.get('ChessCom'),
                        LiChess=row.get('LiChess'),
                        Chess365=row.get('Chess365'),
                        ChessGames=row.get('ChessGames'),
                        ChessResults=row.get('ChessResults')
                    )
                    existing_player = ChessPlayers.query.filter(
                        (ChessPlayers.FideID == fide_player.FideID) | (ChessPlayers.FullName == fide_player.FullName)
                    ).first()

                    if not existing_player:
                        db.session.add(fide_player)

                db.session.commit()
            flash('Players imported successfully', 'success')
            return redirect(url_for('list_players'))
        else:
            flash('Invalid file format. Please upload a CSV file.', 'error')

    return render_template('import_players.html')

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5430)

