import discord
from discord.ext import commands
import sqlite3

from flask import ctx
#from flask import ctx
from convert import csv_to_sqlite
import os
from config import TOKEN, DB_PATH, CSV_PATH

db_file = DB_PATH
csv_file = CSV_PATH

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

#db_file = 'manhwa.db'
#csv_file = 'manhwa.csv'
EMBED_COLOR = discord.Color.blurple()


def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manhwa (
        id INTEGER PRIMARY KEY,
        title TEXT,
        year INTEGER,
        status TEXT,
        genres TEXT,
        chapters INTEGER,
        popularity INTEGER,
        score REAL,
        mean_score REAL,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()
create_table()

class GenreView(discord.ui.View):
    def __init__(self, ctx, results):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.results = results
        self.index = 0

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "!kamu ngga bisa memakai tombol ini!",
                ephemeral=True
            )
            return False
        return True

    async def update_embed(self, interaction):
        row = self.results[self.index]

        embed = discord.Embed(
            title=f"📚 {row['title']}",
            description=(
                f"⭐ Score: {row['score']}\n"
                f"📖 Chapters: {row['chapters'] or 'Unknown'}\n\n"
                f"📄 Halaman {self.index + 1} dari {len(self.results)}"
            ),
            color=EMBED_COLOR
        )

        self.prev_button.disabled = self.index == 0
        self.next_button.disabled = self.index == len(self.results) - 1

        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.message.edit(embed=embed, view=self)


    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.results) - 1:
            self.index += 1
            await self.update_embed(interaction)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command()
async def start(ctx):
    embed = discord.Embed(
        title="👋 Manhwa Database Bot",
        description=(
            "📚 Temukan informasi manhwa dengan cepat dan mudah.\n"
            "📚 Find manhwa information quickly and easily.\n\n"
            "**Available Commands:**"
        ),
        color=EMBED_COLOR
    )

    embed.add_field(
        name="🔍 !manhwa <judul>",
        value="Cari detail manhwa\nFind manhwa details",
        inline=False
    )

    embed.add_field(
        name="🎭 !genre <genre>",
        value="Cari berdasarkan genre\nSearch by genre",
        inline=False
    )

    embed.add_field(
        name="🏆 !top [jumlah]",
        value="Top manhwa berdasarkan score",
        inline=False
    )

    embed.add_field(
        name="🎲 !random_manhwa",
        value="Rekomendasi manhwa acak",
        inline=False
    )

    embed.set_footer(text="Gunakan prefix ! untuk menjalankan perintah")
    embed.set_author(name="Manhwa Database", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

    await ctx.send(embed=embed)


# Command untuk mengimpor data dari CSV ke database SQLite
@bot.command()
@commands.has_permissions(administrator=True)
async def import_data(ctx):
    if not os.path.exists(csv_file):
        await ctx.send(f'❌ CSV file {csv_file} tidak ditemukan.')
        return

    columns = [
        'id', 'title', 'year', 'status',
        'genres', 'chapters', 'popularity',
        'score', 'mean_score', 'description'
    ]

    try:
        csv_to_sqlite(csv_file, db_file, 'manhwa', columns)
        await ctx.send('✅ Data berhasil diimpor ke database!')
    except Exception as e:
        await ctx.send(f'❌ Error: {e}')

@import_data.error
async def import_data_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Kamu tidak punya izin untuk menggunakan command ini.")


# Command untuk mencari manhwa berdasarkan judul
@bot.command()
async def manhwa(ctx, *, title):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM manhwa WHERE title LIKE ?",
        (f"%{title}%",)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        await ctx.send("❌ Manhwa tidak ditemukan.")
        return

    embed = discord.Embed(
        title=f"📚 {row['title']}",
        description=(row["description"][:400] + "...") if row["description"] else "No description available.",
        color=EMBED_COLOR
    )

    embed.add_field(name="📅 Year", value=row["year"], inline=True)
    embed.add_field(name="📖 Chapters", value=row["chapters"], inline=True)
    embed.add_field(name="📌 Status", value=row["status"], inline=True)
    embed.add_field(name="🎭 Genres", value=row["genres"], inline=False)
    embed.add_field(name="⭐ Score", value=row["score"], inline=True)
    embed.add_field(name="📊 Mean Score", value=row["mean_score"], inline=True)

    embed.set_footer(text="Manhwa Database Bot")

    await ctx.send(embed=embed)


# Command untuk mencari manhwa berdasarkan genre
@bot.command()
async def genre(ctx, *, genre_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
    """
    SELECT title, score, chapters
    FROM manhwa WHERE genres LIKE ?
    GROUP BY title 
    ORDER BY score DESC LIMIT 10
    """,
    (f"%{genre_name}%",)
    )

    results = cursor.fetchall()
    conn.close()

    if not results:
        await ctx.send(f"❌ Tidak ada manhwa dengan genre **{genre_name}**.")
        return

    view = GenreView(ctx, results)
    first = results[0]
    #chapters = first["chapters"] or "Unknown"

    embed = discord.Embed(
        title=f"📚 {first['title']}",
        description=(
            f"⭐ Score: {first['score']}\n"
            f"📖 Chapters: {first['chapters'] or 'Unknown'}\n\n"
            f"📄 Halaman 1 dari {len(results)}"
        ),
        color=EMBED_COLOR
    )

    await ctx.send(embed=embed, view=view)


# Command untuk memberikan rekomendasi manhwa secara acak
@bot.command()
async def random_manhwa(ctx):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, score, genres, description FROM manhwa ORDER BY RANDOM() LIMIT 1"
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        await ctx.send("❌ Tidak dapat menemukan manhwa.")
        return

    embed = discord.Embed(
        title="🎲 Random Recommendation",
        description=row["description"][:300] + "...",
        color=discord.Color.green()
    )

    embed.add_field(name="📖 Title", value=row["title"], inline=False)
    embed.add_field(name="🎭 Genres", value=row["genres"], inline=False)
    embed.add_field(name="⭐ Score", value=row["score"], inline=True)

    embed.set_footer(text="Gunakan !random_manhwa lagi untuk rekomendasi baru")

    await ctx.send(embed=embed)

# Command untuk menampilkan top manhwa berdasarkan score
@bot.command()
async def top(ctx, jumlah: int = 5):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, score FROM manhwa GROUP BY title ORDER BY score DESC LIMIT ?",
        (jumlah,)
    )

    results = cursor.fetchall()
    conn.close()

    if not results:
        await ctx.send("❌ Tidak ada data.")
        return

    embed = discord.Embed(
        title="🏆 Top Manhwa",
        color=EMBED_COLOR
    )

    for i, row in enumerate(results, start=1):
        embed.add_field(
            name=f"{i}. {row['title']}",
            value=f"⭐ {row['score']}",
            inline=False
        )

    await ctx.send(embed=embed)


#@bot.command()
#async def Link(ctx):
    #conn = get_db_connection()
    #cursor = conn.cursor()

    #cursor.execute("SELECT link FROM manhwa LIMIT 1")
    #row = cursor.fetchone()
    #conn.close()

    #if row:
    #    await ctx.send(f"🔗 Link: {row['link']}")
    #else:
    #    await ctx.send("❌ Tidak ada link tersedia.")

bot.run(TOKEN)