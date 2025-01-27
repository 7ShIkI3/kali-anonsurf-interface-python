import subprocess
import sys
import os
from getpass import getpass

class VPN:
    def __init__(self, status=False):
        self.ip = ""
        self.localisation = ""
        self.active = status
    
    def set_ip(self, ip):
        self.ip = ip

    def get_ip(self):
        return self.ip if self.ip else "Non disponible"
    
    def set_localisation(self, localisation):
        self.localisation = localisation
    
    def get_localisation(self):
        return self.localisation if self.localisation else "Non disponible"
    
    def set_status(self, status):
        self.active = status
        
    def get_status(self):
        return self.active

def check_root():
    """Vérification et élévation des privilèges"""
    if os.geteuid() != 0:
        print("\n[!] L'application nécessite les privilèges root")
        try:
            password = getpass("Mot de passe sudo : ")
            subprocess.run(
                ['sudo', '-S', 'true'],
                input=password.encode(),
                check=True,
                stderr=subprocess.PIPE
            )
            os.execlp('sudo', 'sudo', sys.executable, __file__)
        except subprocess.CalledProcessError as e:
            print(f"\n[!] Erreur : {e.stderr.decode().strip()}")
            sys.exit(1)

def execute_command(command):
    """Exécution sécurisée des commandes Anonsurf"""
    try:
        result = subprocess.run(
            ['sudo', 'anonsurf', command],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Erreur : {e.stderr.strip()}")
        return None

def ip_formating(ipBrut):
    """Mise affichage de l'ip"""
    ip = ""
    count = 0
    for element in ipBrut:
        if element in ["0","1","2","3","4","5","6","7","8","9","."] and count < 15:
            ip += element
            count += 1
    if len(ip.split('.')) < 4:  
        return "No Visible IP"
    tmp = ip.split('.')
    valid_octets = []
    for element in tmp:
        if element.isdigit():
            num = int(element)
            while num > 255:
                num = num // 10  
            if 0 <= num <= 255:
                valid_octets.append(str(num))
            else:
                valid_octets.append("0")
        else:
            valid_octets.append("0") 
    try:
        final_ip = ".".join(valid_octets[:4]) 
        if final_ip.count('.') != 3:
            return "No Visible IP"     
        return final_ip  
    except:
        return "No Visible IP"

def ip_location(ip):
    """Récupération de la localisation de l'IP"""
    try:
        result = subprocess.run(
            ['curl', f'https://ipapi.co/{ip}/json/'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Erreur : {e.stderr.strip()}")
        return None

def clear_consol():
    subprocess.run(["clear"])

def show_status(vpn):
    """Affichage dynamique du statut"""
    print("\n" + "=" * 40)
    print(f"ANONSURF VPN - Statut : {'🟢 Actif' if vpn.get_status() else '🔴 Inactif'}")
    print(f"IP Actuelle : {vpn.get_ip()}")
    print(f"Localisation : {ip_location(vpn.get_ip())}")
    print("=" * 40)

def main_menu(vpn):
    """Interface utilisateur principale"""
    while True:
        clear_consol()
        show_status(vpn)
        print("\nOptions :")
        print("1. Activer le VPN")
        print("2. Désactiver le VPN")
        print("3. Changer l'IP")
        print("4. Voir son IP")
        print("9. Quitter\n")
        
        try:
            choix = input("Choix > ")
            
            if choix == '1':
                if execute_command('start'):
                    vpn.set_status(True)
                    ip = execute_command('myip')
                    if ip:
                        newIP = ip_formating(ip)
                        vpn.set_ip(newIP)
            elif choix == '2':
                if execute_command('stop'):
                    vpn.set_status(False)
                    ip = execute_command('myip')
                    if ip:
                        newIP = ip_formating(ip)
                        vpn.set_ip(newIP)
            elif choix == '3':
                execute_command('change')
                ip = execute_command('myip')
                if ip:
                    newIP = ip_formating(ip)
                    vpn.set_ip(newIP)
            elif choix == '4':
                ip = execute_command('myip')
                if ip:
                    newIP = ip_formating(ip)
                    vpn.set_ip(newIP)
            elif choix == '9':
                execute_command('stop')
                print("\n[✓] Déconnexion propre effectuée")
                sys.exit()
            else:
                print("[!] Option invalide")
                
        except KeyboardInterrupt:
            print("\n[!] Interruption utilisateur")
            execute_command('stop')
            sys.exit()

if __name__ == "__main__":
    check_root()
    vpn = VPN()
    
    try:
        # Initialisation de l'IP
        ip = execute_command('myip')
        if ip:
            newIP = ip_formating(ip)
            vpn.set_ip(newIP)
        main_menu(vpn)
    except Exception as e:
        print(f"[!] Erreur critique : {str(e)}")
        execute_command('stop')
        sys.exit(1)