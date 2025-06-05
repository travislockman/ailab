#!/bin/bash

echo "[1/5] Resetting kubeadm..."
sudo kubeadm reset -f

echo "[2/5] Cleaning up kubelet, CNI, and Kubernetes directories..."
sudo rm -rf /etc/cni/net.d /opt/cni/bin /var/lib/cni \
            /var/lib/kubelet /etc/kubernetes /var/run/cilium

echo "[3/5] Disabling swap and setting kernel params..."
sudo swapoff -a
sudo sed -i.bak '/ swap / s/^/#/' /etc/fstab

sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables=1
net.ipv4.ip_forward=1
EOF

sudo sysctl --system

echo "[4/5] Making sure containerd is using systemd cgroup driver..."
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd

echo "[5/5] Ready to join the cluster. Run the kubeadm join command here."
