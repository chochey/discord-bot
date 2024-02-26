from discord.ext import commands
import subprocess
import os
import asyncio
from allowed_users import ALLOWED_USERS

def allowed_users():
    async def predicate(ctx):
        if ctx.author.id not in ALLOWED_USERS:
            await ctx.send("You are not authorized to use this command. Ask Nick to be added")
            return False
        return True
    return commands.check(predicate)

class PalworldCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='palworldrestartserver')
    @allowed_users()
    async def restart_server(self, ctx):
        process_name = "PalServer-Win64-Test-Cmd.exe"
        server_process_name = "PalServer.exe"
        batch_file_path = r'C:\Users\blue\Desktop\steam-servers\Start_Palworld_Server.bat'
        working_directory = r'C:\Users\blue\Desktop\steam-servers'
        try:
            subprocess.run(f"taskkill /f /im {process_name}", shell=True)
            await ctx.send("Palworld Server stopping...")
            await asyncio.sleep(2)
            await ctx.send("Palworld Starting Server...")
            subprocess.Popen([batch_file_path], cwd=working_directory, shell=True)
            await asyncio.sleep(30)  # Allow time for the server to restart
            check_process = subprocess.Popen("tasklist", stdout=subprocess.PIPE, shell=True)
            output, error = check_process.communicate()
            if server_process_name in output.decode():
                await ctx.send("Palworld Server is now running.")
            else:
                await ctx.send("Failed to start Palworld Server.")
        except Exception as e:
            await ctx.send(f"Error occurred: {e}")

    @commands.command(name='palworldserverstatus')
    @allowed_users()
    async def server_status(self, ctx):
        server_process_name = "PalServer.exe"
        check_process = subprocess.Popen("tasklist", stdout=subprocess.PIPE, shell=True)
        output, error = check_process.communicate()
        if server_process_name in output.decode():
            await ctx.send("Palworld Server is currently running.")
        else:
            await ctx.send("Palworld Server is not running.")

    @commands.command(name='palworldbackup')
    @allowed_users()
    async def backup(self, ctx):
        powershell_script = """
        $sourceFolder = "C:\\Users\\blue\\Desktop\\steam-servers\\steamapps\\common\\PalServer\\Pal\\Saved\\SaveGames\\0"
        $backupRootFolder = "C:\\Users\\blue\\Desktop\\Palworld_backup_save"
        $backupFolderName = (Get-Date -Format "Backup yyyy-MM-dd_HH-mm-ss")
        $backupFolder = Join-Path $backupRootFolder $backupFolderName

        # Create a new backup
        Copy-Item -Path $sourceFolder -Destination $backupFolder -Recurse

        # Get list of backup folders sorted by creation time
        $backupFolders = Get-ChildItem -Path $backupRootFolder | Where-Object { $_.PSIsContainer } | Sort-Object CreationTime -Descending

        # Keep only the last 20 backups, delete others
        if ($backupFolders.Count -gt 20) {
            $oldBackups = $backupFolders | Select-Object -Skip 20
            foreach ($folder in $oldBackups) {
                Remove-Item -Path $folder.FullName -Recurse -Force
            }
        }
        """
        try:
            subprocess.run(["powershell", "-Command", powershell_script], check=True)
            await ctx.send("Backup created successfully.")
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Error occurred during backup: {e}")

    @commands.command(name='palworldlistbackups')
    @allowed_users()
    async def list_backups(self, ctx):
        backup_root_folder = r"C:\Users\blue\Desktop\Palworld_backup_save"
        try:
            backup_folders = [f.name for f in os.scandir(backup_root_folder) if f.is_dir()]
            if backup_folders:
                backup_list = '\n'.join(backup_folders)
                await ctx.send(f"Available backups:\n{backup_list}")
            else:
                await ctx.send("No backups available.")
        except Exception as e:
            await ctx.send(f"Error occurred while listing backups: {e}")

    @commands.command(name='palworldrestorebackup')
    @allowed_users()
    async def restore_backup(self, ctx, *, backup_name_partial: str):
        source_folder = r"C:\Users\blue\Desktop\steam-servers\steamapps\common\PalServer\Pal\Saved\SaveGames\\0"
        backup_root_folder = r"C:\Users\blue\Desktop\Palworld_backup_save"
        try:
            backup_folders = [f.name for f in os.scandir(backup_root_folder) if f.is_dir()]
            matching_backups = [backup for backup in backup_folders if backup_name_partial.lower() in backup.lower()]
            if len(matching_backups) == 1:
                backup_folder = os.path.join(backup_root_folder, matching_backups[0])
                subprocess.run(f"rd /s /q {source_folder}", shell=True)
                subprocess.run(f"xcopy {backup_folder} {source_folder} /s /e", shell=True)
                await ctx.send(f"Restored backup: {matching_backups[0]}")
            elif len(matching_backups) > 1:
                await ctx.send("Multiple backups matched your input. Please be more specific.")
            else:
                await ctx.send("No backups matched your input. Please try again.")
        except Exception as e:
            await ctx.send(f"Error occurred during restoration: {e}")

async def setup(bot):
    await bot.add_cog(PalworldCommands(bot))
