# Divot & Co — Golf Tips & Gear

The landing page for **Divot & Co**, a new golf brand building gear for the way everyday golfers actually play.

While the online store is being built, this site introduces the brand, shares the daily golf tips we post on Instagram ([@divotcogolf](https://www.instagram.com/divotcogolf/)), and collects people who want first access at launch.

## What's on the page

| Section | Content |
| --- | --- |
| Hero | Brand promise, "Launching soon", links to the waitlist and Instagram |
| Daily tips | Six short golf tips from our Instagram series |
| Story | Why the brand is called Divot & Co and what it stands for |
| Instagram | A preview grid linking to @divotcogolf |
| First access | Waitlist sign-up, or a "Follow on Instagram" button until the waitlist is switched on |

## Project structure

```
.
├── index.html            # The landing page
└── assets
    ├── css/style.css     # Styles (brand colors, layout, responsive rules)
    ├── js/main.js        # Footer year + waitlist form
    └── img/logo.svg      # Logo / favicon
```

Plain HTML, CSS and JavaScript. No build step and no dependencies.

## Run it locally

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Publish with GitHub Pages

1. In the repository, go to **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Pick the `main` branch and the `/ (root)` folder, then **Save**.
4. After a minute the site is live at `https://wangningran.github.io/UI_Design/`.

Put that link in the Instagram bio once it is live.

## Turn on the email waitlist

The page is static, so emails need a form service to collect them. Until one is set up, the "First access" section shows a **Follow on Instagram** button instead of a form.

1. Create a free form at a service such as [Formspree](https://formspree.io/) and copy its endpoint URL.
2. In `assets/js/main.js`, set:
   ```js
   const WAITLIST_ENDPOINT = "https://formspree.io/f/your-form-id";
   ```
3. Commit and push. The email form appears automatically.

## Brand basics

| Token | Value | Use |
| --- | --- | --- |
| Fairway green | `#1f3d2b` | Primary, buttons, dark sections |
| Leaf green | `#2f5d3a` | Links, hover states |
| Cream | `#f4efe4` | Light backgrounds |
| Sand | `#d9a441` | Accents, labels |
| Fonts | Fraunces (headings), Inter (body) | Loaded from Google Fonts |

## Credits

Photos are from [Unsplash](https://unsplash.com/) and are credited in the page footer: Mike Cox, Allan Nygren, Soheb Zaidi, Frederik Rosar, Thomas Park, Imtiaz, Benny Hassum and Bryce Wendler.
