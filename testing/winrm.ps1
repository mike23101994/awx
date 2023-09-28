echo "opening windows firewall for winrm 5985"
New-NetFirewallRule -Name winrm-unencrypted -DisplayName 'Win RM Unencrypted' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 5985;
echo "setting basic winrm auth";
winrm set winrm/config/service/auth '@{Basic="true"}';
echo "setting unencrypted winrm";
winrm set winrm/config/service '@{AllowUnencrypted="true"}';
Enable-NetFirewallRule -Name 'WINRM-HTTP-In-TCP';
Enable-NetFirewallRule -Name 'WINRM-HTTP-In-TCP-PUBLIC';
Enable-NetFirewallRule -Name 'CoreNet-Diag-ICMP4-EchoRequest-In';
Enable-NetFirewallRule -Name 'CoreNet-Diag-ICMP4-EchoRequest-In-NoScope';