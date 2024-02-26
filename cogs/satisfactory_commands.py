from discord.ext import commands
import subprocess
import os
import asyncio
from allowed_users import ALLOWED_USERS

SERVER_NAME = "Satisfactory"


def allowed_users():
    async def predicate(ctx):
        if ctx.author.id not in ALLOWED_USERS:
            await ctx.send("You are not authorized to use this command. Ask Nick to be added")
            return False
        return True
    return commands.check(predicate)

class SatisfactoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name=f'{SERVER_NAME.lower()}restartserver')
    @allowed_users()
    async def restart_server(self, ctx):
        process_name = "UnrealServer-Win64-Shipping.exe"
        server_process_name = "UnrealServer-Win64-Shipping.exe"
        batch_file_path = r'C:\gameservers\satisfactoryserver\satisfactory-server-start.bat'
        working_directory = r'C:\gameservers\satisfactoryserver'
        try:
            subprocess.run(f"taskkill /f /im {process_name}", shell=True)
            await ctx.send("Server stopping...")
            subprocess.Popen([batch_file_path], cwd=working_directory, shell=True)
            await ctx.send("Server restarting...")
            await asyncio.sleep(30)
            check_process = subprocess.Popen("tasklist", stdout=subprocess.PIPE, shell=True)
            output, error = check_process.communicate()
            if server_process_name in output.decode():
                await ctx.send(f"{SERVER_NAME} Server is now running.")
            else:
                await ctx.send(f"Failed to start {SERVER_NAME} Server.")
        except Exception as e:
            await ctx.send(f"Error occurred: {e}")

    @commands.command(name=f'{SERVER_NAME.lower()}serverstatus')
    @allowed_users()
    async def server_status(self, ctx):
        server_process_name = "UnrealServer-Win64-Shipping.exe"
        check_process = subprocess.Popen("tasklist", stdout=subprocess.PIPE, shell=True)
        output, error = check_process.communicate()
        if server_process_name in output.decode():
            await ctx.send(f"{SERVER_NAME} Server is currently running.")
        else:
            await ctx.send(f"{SERVER_NAME} Server is not running.")

    @commands.command(name=f'{SERVER_NAME.lower()}backup')
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
            await ctx.send(f"Backup created successfully for {SERVER_NAME} Server.")
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Error occurred during backup: {e}")

    @commands.command(name=f'{SERVER_NAME.lower()}listbackups')
    @allowed_users()
    async def list_backups(self, ctx):
        backup_root_folder = r"C:\Users\blue\Desktop\Palworld_backup_save"
        try:
            backup_folders = [f.name for f in os.scandir(backup_root_folder) if f.is_dir()]
            backup_list = '\n'.join(backup_folders)
            await ctx.send(f"Available backups for {SERVER_NAME} Server:\n{backup_list}")
        except Exception as e:
            await ctx.send(f"Error occurred while listing backups: {e}")

    @commands.command(name=f'{SERVER_NAME.lower()}restorebackup')
    @allowed_users()
    async def restore_backup(self, ctx, *, backup_name_partial: str):
        source_folder = r"C:\Users\blue\AppData\Local\FactoryGame\Saved\SaveGames\server"
        backup_root_folder = r"C:\Users\blue\Desktop\satisfactory_backup_save"
        try:
            backup_folders = [f.name for f in os.scandir(backup_root_folder) if f.is_dir()]
            matching_backups = [backup for backup in backup_folders if backup_name_partial.lower() in backup.lower()]
            if len(matching_backups) == 1:
                backup_folder = os.path.join(backup_root_folder, matching_backups[0])
                subprocess.run(f"rd /s /q {source_folder}", shell=True)
                subprocess.run(f"xcopy {backup_folder} {source_folder} /s /e", shell=True)
                await ctx.send(f"Restored backup: {matching_backups[0]} for {SERVER_NAME} Server.")
            elif len(matching_backups) > 1:
                await ctx.send(f"Multiple backups matched your input. Please be more specific for {SERVER_NAME} Server:\n" + "\n".join(matching_backups))
            else:
                await ctx.send(f"No backups matched your input for {SERVER_NAME} Server. Please try again.")
        except Exception as e:
            await ctx.send(f"Error occurred during restoration: {e}")

    @commands.command(name='satisfactoryblueprintupload')
    @allowed_users()
    async def upload_to_server(self, ctx):

        # Check if any file is attached to the message
        if len(ctx.message.attachments) == 0:
            await ctx.send("No file attached.")
            return

        # Check if too many files are attached
        if len(ctx.message.attachments) > 20:
            await ctx.send("You can upload a maximum of 20 files at a time.")
            return

        # Process each attachment
        for attachment in ctx.message.attachments:
            filename = attachment.filename
            file_path = os.path.join(os.getcwd(), filename)

            # Check if the filename ends with ".sbp" or ".sbpcfg"
            if not (filename.endswith('.sbp') or filename.endswith('.sbpcfg')):
                await ctx.send(f"File '{filename}' is not allowed. Only files with extensions .sbp or .sbpcfg are allowed.")
                continue

            # Download the file
            await attachment.save(file_path)

            # Scan the file with Windows Defender
            try:
                subprocess.run(['cmd', '/c', 'start', 'cmd', '/c', 'MpCmdRun.exe', '-Scan', '-File', file_path])
            except Exception as e:
                await ctx.send(f"Error occurred while scanning the file '{filename}': {e}")
                os.remove(file_path)
                continue

            # Transfer the file to the Satisfactory server directory
            server_directory = r'C:\Users\blue\AppData\Local\FactoryGame\Saved\SaveGames\blueprints'
            try:
                # Move the file to the server directory
                os.replace(file_path, os.path.join(server_directory, filename))
                await ctx.send(f"File '{filename}' uploaded and transferred the blueprint successfully.")
            except Exception as e:
                await ctx.send(f"Error occurred while transferring the file '{filename}': {e}")
                os.remove(file_path)
                continue

async def setup(bot):
    await bot.add_cog(SatisfactoryCommands(bot))
