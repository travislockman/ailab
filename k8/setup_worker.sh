#!/bin/bash
# 1. Disable swap (required by kubelet)
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# 2. Load kernel modules
sudo modprobe br_netfilter

# 3. Configure sysctl for networking
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables=1
net.ipv4.ip_forward=1
EOF

# 4. Apply sysctl settings
sudo sysctl --system

# 5. Install containerd
sudo apt update
sudo apt install -y containerd

# 6. Create containerd default config
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# Set containerd to use systemd cgroup driver (recommended for Cilium too)
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml


# 7. Restart containerd
sudo systemctl restart containerd
sudo systemctl enable containerd

# 8. Add Kubernetes apt repo
sudo apt install -y apt-transport-https ca-certificates curl gpg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# 9. Install kubelet, kubeadm, and kubectl
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# 10. (Optional but recommended) Set hostname
# sudo hostnamectl set-hostname worker-node-1

# 11. Reboot (optional if kernel modules weren’t loaded properly)
# sudo reboot

# 12. Join the cluster (replace with your actual token/hash from the control plane)
sudo kubeadm join <CONTROL_PLANE_IP>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
