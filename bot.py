import discord
from discord import app_commands
import os

# ===== トークン（Renderの環境変数から取得）=====
TOKEN = os.getenv("DISCORD_TOKEN")

# ===== intents =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ===== 計算部分 =====
def calc_patterns(total_players, target_players, group_size=12):
    groups = total_players // group_size
    patterns = []

    for advance in range(1, group_size + 1):
        base = groups * advance
        wildcard = target_players - base

        if wildcard >= 0:
            patterns.append((advance, wildcard))

    return patterns, groups


def get_recommend(patterns):
    good = []
    for a, w in patterns:
        if 3 <= a <= 6 and w <= 12:
            good.append((a, w))

    if not good and patterns:
        return patterns[-1]

    return good[0] if good else None


# ===== スラッシュコマンド =====
@tree.command(name="calc", description="通過人数の組み合わせを計算")
@app_commands.describe(total="現在の人数", target="残したい人数")
async def calc(interaction: discord.Interaction, total: int, target: int):

    if total % 12 != 0:
        await interaction.response.send_message("⚠️ 人数は12の倍数にしてね", ephemeral=True)
        return

    patterns, groups = calc_patterns(total, target)

    if not patterns:
        await interaction.response.send_message("❌ 組み合わせが見つかりません", ephemeral=True)
        return

    embed = discord.Embed(
        title="📊 通過計算結果",
        description=f"{total}人（{groups}組）→ {target}人",
        color=0x00ffcc
    )

    text = ""
    for a, w in patterns:
        text += f"・各組 上位{a}人 + 得点上位{w}人\n"

    embed.add_field(name="全パターン", value=text, inline=False)

    rec = get_recommend(patterns)
    if rec:
        embed.add_field(
            name="⭐ おすすめ",
            value=f"各組 上位{rec[0]}人 + 得点上位{rec[1]}人",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ===== 起動時 =====
@client.event
async def on_ready():
    await tree.sync()
    print(f"ログインしました: {client.user}")


# ===== 起動 =====
client.run(TOKEN)
