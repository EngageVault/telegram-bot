from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import os
import psycopg2
import logging
import csv
from io import StringIO
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import subprocess
import seaborn as sns
from collections import defaultdict
import pandas as pd
import numpy as np

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533
DATABASE_URL = os.getenv("DATABASE_URL")

WELCOME_MESSAGE = """🚀 Welcome to EngageVault!

⭐ Congratulations Early Adopter! ⭐

You've just discovered the next big thing in social media growth - and you're among the first to join! 🎯

💎 Being an early member means:
• EXCLUSIVE ACCESS to premium features
• PRIORITY STATUS for upcoming features
• FREE GIFTS for early supporters

📝 How you'll benefit:
• Boost your social media presence
• Earn real rewards while growing
• Connect with power users
• Get ahead of the competition

⚡ Don't miss out on these early-bird benefits!
Join now before regular rates apply! 🎁

Ready to multiply your social growth? Tap below! 👇"""

# États de la conversation
FEEDBACK = 0

# États pour la réponse
REPLY_ID = 0
REPLY_MESSAGE = 1

# États pour le broadcast
MESSAGE_TEXT = 0

# États pour la restauration
WAITING_FOR_FILE = 0

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Table existante
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                commands INTEGER DEFAULT 1
            )
        ''')
        
        # Nouvelle table pour les feedbacks
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données initialisée")
        return True
    except Exception as e:
        logger.error(f"Erreur BD: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        user_id = user.id
        username = user.username or "Anonymous"

        # Mise à jour des stats
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO bot_stats (user_id, username, commands)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id) DO UPDATE 
            SET commands = bot_stats.commands + 1
        ''', (user_id, username))
        conn.commit()
        cur.close()
        conn.close()

        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"Start command from {username}")
        
    except Exception as e:
        logger.error(f"Erreur start: {str(e)}")
        # Envoyer quand même le message si la BD échoue
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

def get_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Total des commandes
        cur.execute('SELECT SUM(commands) FROM bot_stats')
        total_commands = cur.fetchone()[0] or 0
        
        # Utilisateurs uniques
        cur.execute('SELECT COUNT(*) FROM bot_stats')
        unique_users = cur.fetchone()[0] or 0
        
        # Total des feedbacks
        cur.execute('SELECT COUNT(*) FROM feedbacks')
        total_feedbacks = cur.fetchone()[0] or 0
        
        # Utilisateurs uniques ayant envoyé un feedback
        cur.execute('SELECT COUNT(DISTINCT user_id) FROM feedbacks')
        unique_feedback_users = cur.fetchone()[0] or 0
        
        # Top 5 utilisateurs
        cur.execute('''
            SELECT username, commands 
            FROM bot_stats 
            ORDER BY commands DESC 
            LIMIT 5
        ''')
        top_users = cur.fetchall()
        
        stats_message = f"""📊 Bot Statistics:

Total /start commands: {total_commands}
Unique users: {unique_users}

📬 Feedback Statistics:
Total feedbacks: {total_feedbacks}
Unique users feedback: {unique_feedback_users}

Most active users:"""

        for username, commands in top_users:
            stats_message += f"\n@{username}: {commands} commands"
        
        update.message.reply_text(stats_message)
        logger.info("Stats envoyées")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")
        update.message.reply_text("❌ Error getting statistics")

def feedback_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📝 Thank you for contacting EngageVault support!\n\n"
        "Please send your message below.\n\n"
        "⚠️ Important Security Notice:\n"
        "• Our staff will ONLY respond through THIS bot\n"
        "• Never trust anyone claiming to be EngageVault staff in private messages\n"
        "• All official responses will come directly through this conversation\n\n"
        "You can cancel anytime by sending /cancel"
    )
    return FEEDBACK

def feedback_received(update: Update, context: CallbackContext):
    user = update.effective_user
    feedback_text = update.message.text
    
    try:
        # Sauvegarde en BD
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO feedbacks (user_id, username, message) VALUES (%s, %s, %s)',
            (user.id, user.username or "Anonymous", feedback_text)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Notification à l'admin
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""📬 Nouveau Feedback:

De: @{user.username or 'Anonymous'}
ID: {user.id}

Message:
{feedback_text}"""
        )
        
        # Message de confirmation à l'utilisateur
        update.message.reply_text(
            "✅ Your message has been received!\n\n"
            "If needed, you will receive a response directly through this bot.\n\n"
            "⚠️ Security Reminder:\n"
            "• Our team will NEVER contact you outside of this bot\n"
            "• All official responses will be sent here\n"
            "• Stay safe and ignore any direct messages claiming to be from our staff"
        )
    except Exception as e:
        logger.error(f"Erreur feedback: {str(e)}")
        update.message.reply_text(
            "❌ Sorry, there was an error processing your message.\n"
            "Please try again later."
        )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "❌ Feedback cancelled.\n"
        "Feel free to send your feedback anytime using /feedback"
    )
    return ConversationHandler.END

def reply_start(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return ConversationHandler.END
    
    update.message.reply_text(
        "📤 Reply to User\n\n"
        "Please send the user's ID first\n"
        "(You can find it in the feedback notification)\n\n"
        "Cancel anytime with /cancel"
    )
    return REPLY_ID

def reply_get_id(update: Update, context: CallbackContext):
    try:
        user_id = int(update.message.text)
        context.user_data['reply_to'] = user_id
        
        update.message.reply_text(
            "✅ User ID received.\n\n"
            "Now send your response message:"
        )
        return REPLY_MESSAGE
    except ValueError:
        update.message.reply_text("❌ Invalid ID. Please send a valid user ID or /cancel")
        return REPLY_ID

def reply_send(update: Update, context: CallbackContext):
    user_id = context.user_data.get('reply_to')
    message = update.message.text
    
    try:
        context.bot.send_message(
            chat_id=user_id,
            text=f"""📨 Response from EngageVault Support:

{message}

⚠️ Remember: Our team only communicates through this bot."""
        )
        
        update.message.reply_text("✅ Response sent successfully!")
    except Exception as e:
        logger.error(f"Erreur envoi réponse: {str(e)}")
        update.message.reply_text("❌ Error sending response. Please try again.")
    
    return ConversationHandler.END

def message_start(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return ConversationHandler.END
    
    update.message.reply_text(
        "📢 Broadcast Message\n\n"
        "Please send the message you want to broadcast to all users.\n"
        "Cancel anytime with /cancel"
    )
    return MESSAGE_TEXT

def message_send(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
        
    broadcast_text = update.message.text
    success_count = 0
    fail_count = 0
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer tous les utilisateurs uniques
        cur.execute('SELECT DISTINCT user_id FROM bot_stats')
        users = cur.fetchall()
        
        for user in users:
            try:
                context.bot.send_message(
                    chat_id=user[0],
                    text=f"""📢 Message from EngageVault:

{broadcast_text}

⚠️ Official message sent through this bot only."""
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Erreur envoi broadcast à {user[0]}: {str(e)}")
                fail_count += 1
        
        cur.close()
        conn.close()
        
        # Rapport d'envoi
        update.message.reply_text(
            f"""✅ Broadcast completed!

📊 Statistics:
• Successfully sent: {success_count}
• Failed: {fail_count}
• Total attempted: {success_count + fail_count}"""
        )
        
    except Exception as e:
        logger.error(f"Erreur broadcast: {str(e)}")
        update.message.reply_text("❌ Error sending broadcast message")
    
    return ConversationHandler.END

def get_users(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer les utilisateurs avec leurs stats
        cur.execute('''
            SELECT 
                b.username,
                b.commands,
                COUNT(f.id) as feedback_count
            FROM bot_stats b
            LEFT JOIN feedbacks f ON b.user_id = f.user_id
            GROUP BY b.user_id, b.username, b.commands
            ORDER BY b.commands DESC
            LIMIT 10
        ''')
        users = cur.fetchall()
        
        users_message = """👥 Recent Users:

Username | Commands | Feedbacks
---------------------------"""

        for username, commands, feedback_count in users:
            users_message += f"\n@{username}: {commands} cmds, {feedback_count} fb"
        
        # Statistiques supplémentaires
        cur.execute('SELECT COUNT(*) FROM bot_stats')
        total_users = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM bot_stats WHERE commands > 1')
        returning_users = cur.fetchone()[0]
        
        users_message += f"""

📊 User Statistics:
• Total users: {total_users}
• Returning users: {returning_users}
• Shown above: Top 10 most active"""
        
        update.message.reply_text(users_message)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur users: {str(e)}")
        update.message.reply_text("❌ Error getting user list")

def export_data(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Créer un buffer pour le CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Export des utilisateurs
        cur.execute('''
            SELECT 
                b.user_id,
                b.username,
                b.commands,
                COUNT(f.id) as feedback_count
            FROM bot_stats b
            LEFT JOIN feedbacks f ON b.user_id = f.user_id
            GROUP BY b.user_id, b.username, b.commands
        ''')
        users = cur.fetchall()
        
        # Première partie : Stats utilisateurs
        writer.writerow(['=== USER STATISTICS ==='])
        writer.writerow(['User ID', 'Username', 'Commands', 'Feedbacks'])
        writer.writerows(users)
        writer.writerow([])  # Ligne vide pour séparer
        
        # Deuxième partie : Feedbacks
        cur.execute('''
            SELECT 
                user_id,
                username,
                message,
                created_at
            FROM feedbacks
            ORDER BY created_at DESC
        ''')
        feedbacks = cur.fetchall()
        
        writer.writerow(['=== FEEDBACK HISTORY ==='])
        writer.writerow(['User ID', 'Username', 'Message', 'Date'])
        writer.writerows(feedbacks)
        
        # Troisième partie : Statistiques globales
        cur.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as unique_users,
                SUM(commands) as total_commands
            FROM bot_stats
        ''')
        global_stats = cur.fetchone()
        
        writer.writerow([])
        writer.writerow(['=== GLOBAL STATISTICS ==='])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Unique Users', global_stats[0]])
        writer.writerow(['Total Commands', global_stats[1]])
        writer.writerow(['Total Feedbacks', len(feedbacks)])
        
        cur.close()
        conn.close()
        
        # Préparer le fichier
        output.seek(0)
        date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bot_export_{date}.csv'
        
        # Envoyer le fichier
        context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=output.getvalue().encode(),
            filename=filename,
            caption="📊 Here's your complete bot data export"
        )
        
    except Exception as e:
        logger.error(f"Erreur export: {str(e)}")
        update.message.reply_text("❌ Error generating export")

def create_activity_graph(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer l'activité des 7 derniers jours
        cur.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM feedbacks
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        activity_data = cur.fetchall()
        
        # Préparer les données pour le graphique
        dates = []
        counts = []
        
        # Remplir avec tous les jours, même ceux sans activité
        for i in range(7):
            date = datetime.now().date() - timedelta(days=6-i)
            count = 0
            for d, c in activity_data:
                if d == date:
                    count = c
                    break
            dates.append(date.strftime('%d/%m'))
            counts.append(count)
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        plt.plot(dates, counts, marker='o')
        plt.title('Daily Activity (Last 7 Days)')
        plt.xlabel('Date')
        plt.ylabel('Number of Interactions')
        plt.grid(True)
        plt.xticks(rotation=45)
        
        # Sauvegarder le graphique
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Envoyer le graphique
        update.message.reply_photo(
            photo=buf,
            caption="📊 Activity graph for the last 7 days"
        )
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur activity graph: {str(e)}")
        update.message.reply_text("❌ Error generating activity graph")

def create_growth_graph(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer la croissance des utilisateurs
        cur.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT user_id) as users
            FROM feedbacks
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        growth_data = cur.fetchall()
        
        if not growth_data:
            update.message.reply_text("No data available for growth graph.")
            return
        
        # Préparer les données
        dates = [d.strftime('%d/%m') for d, _ in growth_data]
        users = []
        total = 0
        for _, count in growth_data:
            total += count
            users.append(total)
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        plt.plot(dates, users, marker='o', color='green')
        plt.title('User Growth Over Time')
        plt.xlabel('Date')
        plt.ylabel('Total Users')
        plt.grid(True)
        plt.xticks(rotation=45)
        
        # Sauvegarder le graphique
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Envoyer le graphique
        update.message.reply_photo(
            photo=buf,
            caption=f"📈 Growth graph\nTotal users: {total}"
        )
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur growth graph: {str(e)}")
        update.message.reply_text("❌ Error generating growth graph")

def create_backup(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        # Informer que le backup commence
        status_message = update.message.reply_text("🔄 Creating database backup...")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Créer un fichier SQL
        backup_data = []
        
        # Sauvegarder bot_stats
        cur.execute('SELECT * FROM bot_stats')
        stats_data = cur.fetchall()
        backup_data.append("-- Bot Stats Table\n")
        for row in stats_data:
            backup_data.append(f"INSERT INTO bot_stats (user_id, username, commands) VALUES ({row[0]}, '{row[1]}', {row[2]});\n")
        
        # Sauvegarder feedbacks
        cur.execute('SELECT * FROM feedbacks')
        feedback_data = cur.fetchall()
        backup_data.append("\n-- Feedbacks Table\n")
        for row in feedback_data:
            backup_data.append(f"INSERT INTO feedbacks (id, user_id, username, message, created_at) VALUES ({row[0]}, {row[1]}, '{row[2]}', '{row[3]}', '{row[4]}');\n")
        
        # Créer le fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.sql'
        
        with open(filename, 'w') as f:
            f.write("-- Database Backup\n")
            f.write(f"-- Date: {timestamp}\n\n")
            f.writelines(backup_data)
        
        # Envoyer le fichier
        with open(filename, 'rb') as f:
            context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=filename,
                caption=f"📦 Database Backup\n📅 {timestamp}"
            )
        
        # Nettoyer
        import os
        os.remove(filename)
        
        cur.close()
        conn.close()
        
        # Mettre à jour le message
        status_message.edit_text("✅ Backup completed and sent!")
        
    except Exception as e:
        logger.error(f"Erreur backup: {str(e)}")
        update.message.reply_text(
            "❌ Error creating backup\n"
            "Please check the logs for details."
        )

def restore_start(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return ConversationHandler.END
    
    update.message.reply_text(
        "📥 Please send the .sql backup file you want to restore.\n\n"
        "⚠️ Warning: This will overwrite current data!\n"
        "Cancel anytime with /cancel"
    )
    return WAITING_FOR_FILE

def restore_file(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    
    try:
        # Vérifier si un fichier a été envoyé
        if not update.message.document:
            update.message.reply_text("❌ Please send a .sql file")
            return WAITING_FOR_FILE
        
        # Vérifier l'extension
        if not update.message.document.file_name.endswith('.sql'):
            update.message.reply_text("❌ Only .sql files are accepted")
            return WAITING_FOR_FILE
        
        status_message = update.message.reply_text("🔄 Starting restoration...")
        
        # Télécharger le fichier
        file = context.bot.get_file(update.message.document.file_id)
        sql_content = file.download_as_bytearray().decode('utf-8')
        
        # Connexion à la BD
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Sauvegarder les données actuelles avant restauration
        status_message.edit_text("🔄 Creating backup before restore...")
        create_backup(update, context)
        
        # Vider les tables
        status_message.edit_text("🔄 Clearing current data...")
        cur.execute("DELETE FROM feedbacks")
        cur.execute("DELETE FROM bot_stats")
        
        # Exécuter les requêtes de restauration
        status_message.edit_text("🔄 Restoring data...")
        cur.execute(sql_content)
        conn.commit()
        
        cur.close()
        conn.close()
        
        update.message.reply_text(
            "✅ Restoration completed!\n"
            "Use /stats to verify the data"
        )
        
    except Exception as e:
        logger.error(f"Erreur restore: {str(e)}")
        update.message.reply_text(
            "❌ Error during restoration\n"
            "Previous backup has been kept safe"
        )
    
    return ConversationHandler.END

def analyze_peak_hours(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer les heures d'activité
        cur.execute('''
            SELECT 
                EXTRACT(HOUR FROM created_at) as hour,
                COUNT(*) as count
            FROM feedbacks
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY hour
            ORDER BY hour
        ''')
        
        hours_data = cur.fetchall()
        
        # Préparer les données
        hours = list(range(24))
        counts = [0] * 24
        
        for hour, count in hours_data:
            counts[int(hour)] = count
        
        # Créer le graphique
        plt.figure(figsize=(12, 6))
        sns.barplot(x=hours, y=counts)
        
        plt.title('Peak Hours Analysis (Last 30 Days)')
        plt.xlabel('Hour of Day (24h format)')
        plt.ylabel('Number of Interactions')
        plt.grid(True, alpha=0.3)
        
        # Trouver l'heure de pointe
        peak_hour = hours[counts.index(max(counts))]
        peak_count = max(counts)
        
        # Ajouter une ligne pour l'heure de pointe
        plt.axvline(x=peak_hour, color='r', linestyle='--', alpha=0.5)
        
        # Sauvegarder le graphique
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Calculer les statistiques
        total_interactions = sum(counts)
        avg_per_hour = total_interactions / 24
        
        # Trouver les 3 heures les plus actives
        top_hours = sorted([(h, c) for h, c in zip(hours, counts)], 
                         key=lambda x: x[1], 
                         reverse=True)[:3]
        
        # Envoyer le graphique avec les stats
        caption = f"""📊 Peak Hours Analysis (Last 30 Days)

🔥 Most Active Hours:
1. {top_hours[0][0]:02d}:00 - {top_hours[0][1]} interactions
2. {top_hours[1][0]:02d}:00 - {top_hours[1][1]} interactions
3. {top_hours[2][0]:02d}:00 - {top_hours[2][1]} interactions

📈 Statistics:
• Total interactions: {total_interactions}
• Average per hour: {avg_per_hour:.1f}
• Peak hour: {peak_hour:02d}:00 ({peak_count} interactions)"""
        
        update.message.reply_photo(
            photo=buf,
            caption=caption
        )
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur peak analysis: {str(e)}")
        update.message.reply_text("❌ Error analyzing peak hours")

def analyze_retention(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer les données d'utilisation
        cur.execute('''
            SELECT 
                user_id,
                username,
                MIN(created_at) as first_seen,
                MAX(created_at) as last_seen,
                COUNT(*) as total_interactions
            FROM feedbacks
            GROUP BY user_id, username
            ORDER BY first_seen
        ''')
        
        user_data = cur.fetchall()
        
        if not user_data:
            update.message.reply_text("No data available for retention analysis.")
            return
        
        # Préparer les données
        retention_data = {
            '1_day': 0,
            '7_days': 0,
            '30_days': 0
        }
        
        total_users = len(user_data)
        now = datetime.now()
        
        for user in user_data:
            first_seen = user[2]
            last_seen = user[3]
            delta = last_seen - first_seen
            
            if delta.days >= 1:
                retention_data['1_day'] += 1
            if delta.days >= 7:
                retention_data['7_days'] += 1
            if delta.days >= 30:
                retention_data['30_days'] += 1
        
        # Créer le graphique
        periods = ['1 Day', '7 Days', '30 Days']
        rates = [
            (retention_data['1_day'] / total_users) * 100,
            (retention_data['7_days'] / total_users) * 100,
            (retention_data['30_days'] / total_users) * 100
        ]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(periods, rates)
        
        # Ajouter les pourcentages sur les barres
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')
        
        plt.title('User Retention Analysis')
        plt.xlabel('Time Period')
        plt.ylabel('Retention Rate (%)')
        plt.ylim(0, 100)
        
        # Sauvegarder le graphique
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Statistiques supplémentaires
        avg_interactions = sum(u[4] for u in user_data) / total_users
        active_last_week = sum(1 for u in user_data if (now - u[3]).days <= 7)
        
        caption = f"""📊 Retention Analysis

🔄 Retention Rates:
• After 1 day: {rates[0]:.1f}%
• After 7 days: {rates[1]:.1f}%
• After 30 days: {rates[2]:.1f}%

📈 Additional Stats:
• Total users analyzed: {total_users}
• Average interactions per user: {avg_interactions:.1f}
• Active users (last 7 days): {active_last_week}

ℹ️ This analysis shows how many users remain active after their first interaction."""
        
        update.message.reply_photo(
            photo=buf,
            caption=caption
        )
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur retention analysis: {str(e)}")
        update.message.reply_text("❌ Error analyzing retention")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():
        try:
            updater = Updater(TOKEN)
            dp = updater.dispatcher
            
            # Handlers existants
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("stats", get_stats))
            
            # Nouveau handler pour feedback
            feedback_handler = ConversationHandler(
                entry_points=[CommandHandler('feedback', feedback_start)],
                states={
                    FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, feedback_received)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            dp.add_handler(feedback_handler)
            
            # Ajouter le handler pour les réponses
            reply_handler = ConversationHandler(
                entry_points=[CommandHandler('reply', reply_start)],
                states={
                    REPLY_ID: [MessageHandler(Filters.text & ~Filters.command, reply_get_id)],
                    REPLY_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, reply_send)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            dp.add_handler(reply_handler)
            
            # Ajouter le handler pour le broadcast
            message_handler = ConversationHandler(
                entry_points=[CommandHandler('message', message_start)],
                states={
                    MESSAGE_TEXT: [MessageHandler(Filters.text & ~Filters.command, message_send)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            dp.add_handler(message_handler)
            
            # Ajouter le handler pour users
            dp.add_handler(CommandHandler("users", get_users))
            
            # Ajouter le handler pour export
            dp.add_handler(CommandHandler("export", export_data))
            
            # Ajouter les handlers pour les graphiques
            dp.add_handler(CommandHandler("activity", create_activity_graph))
            dp.add_handler(CommandHandler("growth", create_growth_graph))
            
            # Ajouter le handler pour backup
            dp.add_handler(CommandHandler("backup", create_backup))
            
            # Ajouter le handler pour restore
            restore_handler = ConversationHandler(
                entry_points=[CommandHandler('restore', restore_start)],
                states={
                    WAITING_FOR_FILE: [MessageHandler(Filters.document, restore_file)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            dp.add_handler(restore_handler)
            
            # Ajouter le handler pour peak
            dp.add_handler(CommandHandler("peak", analyze_peak_hours))
            
            # Ajouter le handler pour retention
            dp.add_handler(CommandHandler("retention", analyze_retention))
            
            logger.info("Bot prêt à démarrer")
            updater.start_polling()
            updater.idle()
        except Exception as e:
            logger.error(f"Erreur critique au démarrage: {str(e)}")
    else:
        logger.error("Échec de l'initialisation de la base de données")