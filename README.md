# TP Kubernetes - Cours Data DevOps - Enseirb-Matmeca

```bash
brew install git-lfs
git clone git@github.com:rqueraud/cours_kubernetes.git
```

Placez le fichier `service-account.json`à la racine du projet.

Pour builder les images : 
```bash
docker build -t 2024_kubernetes_post_pusher -f ./post_pusher/Dockerfile .
docker build -t 2024_kubernetes_post_api -f ./post_api/Dockerfile .
```

Pour executer les images :
```bash
docker run 2024_kubernetes_post_pusher
docker run -p 8000:8000 2024_kubernetes_post_api
```