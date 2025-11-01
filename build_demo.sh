#!/bin/bash
set -e

echo "🔨 Building React demo interface..."

cd demo

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Builder l'interface
echo "🏗️  Building interface..."
npm run build

echo "✅ Build completed! Interface available in demo/dist/"

