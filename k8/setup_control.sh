#!/bin/bash
# Kubernetes Control Plane Setup Script (Ubuntu 22.04+)
# CNI: Cilium with pod-network-cidr 172.10.10.0/24

# 1. Disable swap (required for Kubernetes)
sudo swapoff -a
sudo sed -i.bak '/ swap / s/^/#/' /etc/fstab

# 2. Enable iptables bridging (required for CNIs like Cilium)
sudo modprobe br_netfilter

# Set required kernel parameters
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables=1
net.ipv4.ip_forward=1
EOF

# Apply the sysctl settings
sudo sysctl --system

# 3. Install containerd (Kubernetes CRI runtime)
sudo apt update
sudo apt install -y containerd

# Create containerd default config
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null

# Use systemd as the cgroup driver (recommended for kubelet)
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# Restart and enable containerd
sudo systemctl restart containerd
sudo systemctl enable containerd

# 4. Add Kubernetes repository
sudo apt-get install -y curl apt-transport-https gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# 5. Initialize the control plane using Cilium-compatible CIDR
sudo kubeadm init --pod-network-cidr=172.10.10.0/24

# 6. Set up kubeconfig for kubectl access as current user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 7. Install Cilium CLI (latest version)
export CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
export CILIUM_CLI_ARCH=amd64
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CILIUM_CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CILIUM_CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CILIUM_CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CILIUM_CLI_ARCH}.tar.gz{,.sha256sum}

# 8. Deploy Cilium CNI with the matching pod CIDR
cilium install --cluster-name default --operator-namespace kube-system --ipv4-native-routing-cidr 172.10.10.0/24

# DONE. Validate with:
# kubectl get nodes
# kubectl get pods -n kube-system
# cilium status

# To join worker or secondary control plane:
# Run the join command shown after kubeadm init, or retrieve it anytime with:
# kubeadm token create --print-join-command
