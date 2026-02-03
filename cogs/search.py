import discord
from discord.ext import commands
from discord import app_commands
from files import search


class Paginator(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.current = 0
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current == 0  # <
        self.children[1].disabled = self.current == len(self.embeds) - 1  # >

    @discord.ui.button(emoji="◀", style=discord.ButtonStyle.gray)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current -= 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.embeds[self.current], view=self
        )

    @discord.ui.button(emoji="▶", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.embeds[self.current], view=self
        )


class Search(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="search", description="search epstein files")
    async def search(self, inter: discord.Interaction, input: str):
        await inter.response.defer()
        result = await search(input)
        embeds = []
        for hit in result:
            em = discord.Embed(
                title=f"Document ID: {hit.source.document_id}",
                description=f"{hit.source.origin_file_uri}\n{hit.content}",
            )
            em.set_footer(
                text=f"name:{hit.source.origin_file_name} | indexed at:{hit.source.indexed_at}"
            )
            embeds.append(em)
        if len(embeds) == 0:
            embed = discord.Embed(
                title="No results found",
                description=f'Looks like `"{input}"` are not in epstein files.',
                color=discord.Color.red(),
            )
            return await inter.followup.send(embed=embed)
        view = Paginator(embeds)
        await inter.followup.send(embed=embeds[0], view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))
