import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True  # To allow the bot to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Ticket category name and channel name prefix
TICKET_CATEGORY_NAME = "Tickets"
TICKET_CHANNEL_PREFIX = "ticket-"

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')

# Command to create a ticket
@bot.command()
async def create_ticket(ctx):
    # Check if the user already has a ticket
    existing_ticket = discord.utils.get(ctx.guild.text_channels, name=f'{TICKET_CHANNEL_PREFIX}{ctx.author.id}')
    if existing_ticket:
        await ctx.send(f'{ctx.author.mention}, you already have an open ticket: {existing_ticket.mention}')
        return

    # Create the ticket channel
    category = discord.utils.get(ctx.guild.categories, name=TICKET_CATEGORY_NAME)
    if not category:
        category = await ctx.guild.create_category(TICKET_CATEGORY_NAME)

    ticket_channel = await ctx.guild.create_text_channel(f'{TICKET_CHANNEL_PREFIX}{ctx.author.id}', category=category)
    await ticket_channel.set_permissions(ctx.guild.default_role, send_messages=False)  # Lock channel for everyone
    await ticket_channel.set_permissions(ctx.author, send_messages=True)  # Allow the user to send messages

    await ticket_channel.send(f'{ctx.author.mention}, welcome to your ticket! How can we assist you?')

    # Add a button for staff to close the ticket
    close_button = Button(label="Close Ticket", style=discord.ButtonStyle.danger)

    async def close_ticket_callback(interaction):
        await ticket_channel.send(f'{interaction.user.mention} has closed the ticket.')
        await ticket_channel.delete()

    close_button.callback = close_ticket_callback
    view = View()
    view.add_item(close_button)
    await ticket_channel.send("Click the button to close the ticket.", view=view)

    await ctx.send(f'{ctx.author.mention}, your ticket has been created: {ticket_channel.mention}')

# Command to view open tickets (for staff)
@bot.command()
async def open_tickets(ctx):
    tickets = [channel for channel in ctx.guild.text_channels if channel.name.startswith(TICKET_CHANNEL_PREFIX)]
    if not tickets:
        await ctx.send('No open tickets.')
    else:
        ticket_list = '\n'.join([channel.mention for channel in tickets])
        await ctx.send(f'Open tickets:\n{ticket_list}')

# Run the bot with your token
bot.run('YOUR_BOT_TOKEN')
