# bdc_promotions (static HTML + JS starter)

This repository contains a minimal static webshop scaffold that uses:

- index.html — frontend (HTML + vanilla JS) that loads `data/products.json`.
- data/products.json — product catalog (edit manually or use the provided Python script).
- scripts/add_product.py — small Python helper to append a product to the catalog.
- .github/workflows/deploy-pages.yml — GitHub Actions workflow that copies files into `public/` and deploys them to GitHub Pages (no Ruby required).

How to use (quick):
1. Clone the repo and add the files (instructions below).
2. Optionally enable Snipcart for a hosted cart:
   - Sign up at https://snipcart.com
   - Un-comment the Snipcart script/div in `index.html` and replace YOUR_SNIPCART_PUBLIC_KEY with your public key.
   - Snipcart public key can be used directly in frontend; do not put secret keys in client code.
3. Push to `main`. The workflow will run on push and deploy to GitHub Pages.

Commands to add these files locally and push (example):
```bash
# 1. Clone
git clone https://github.com/jaap-dekkinga/bdc_promotions.git
cd bdc_promotions

# 2. Create a branch (recommended)
git checkout -b scaffold/static-shop

# 3. Add the files (copy the content blocks into the corresponding paths shown above)
#    e.g., create .github/workflows/deploy-pages.yml, index.html, data/products.json, scripts/add_product.py, .gitignore, README.md

# 4. Add, commit, and push
git add .
git commit -m "Add static webshop scaffold (HTML+JS+Python) and Pages deploy workflow"
git push -u origin scaffold/static-shop

# 5. Create a Pull Request on GitHub and merge to main,
#    or push directly to main if you prefer.
```

Notes and next steps
- The workflow uses the GitHub Pages Actions approach (it builds a `public/` artifact and deploys from it).
- If you plan to accept card payments, Snipcart is the easiest hosted option for a static site. Stripe Checkout is possible but requires a secure server-side endpoint to create sessions (can be hosted on Vercel/Netlify/AWS).
- If you want me to push these files for you, grant me write access to the repository (or provide a personal access token with repo write permission). Once I have permission I will push the scaffold and confirm the first deployment.
- If you prefer, I can instead scaffold a small Pelican (Python SSG) or Eleventy (Node) site — tell me which.
