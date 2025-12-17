# 🚀 NORSK DRILL v2.0 - DEPLOYMENT PACKAGE

## 📦 Какво съдържа този пакет?

Това е **comprehensive update** на Norsk Drill приложението с **5 major функционалности**:

✅ **Validation Fix** - Празни полета = грешни отговори  
✅ **Parentheses Ignore** - Игнорира текст в скоби  
✅ **Duplicate Checking** - Пропуска дубликати при импорт  
✅ **Edit Functionality** - Редактиране на всички думи  
✅ **Phrases (NEW!)** - Нова категория за фрази и изрази  

---

## 📚 ДОКУМЕНТАЦИЯ (Прочети ПЪРВО!)

### 🎯 Главен Guide:
**START HERE:** `DEPLOYMENT_GUIDE.md`  
- Пълна стъпка-по-стъпка инструкция
- Troubleshooting
- Testing

### 📋 File Mapping:
**FILE_MAPPING.md**  
- Списък на всички файлове
- Къде отива всеки файл
- Batch copy команди
- Checklist

### 🔧 Admin Changes:
**admin_py_changes.md**  
- Детайлни промени в admin.py
- Code snippets
- Alternative methods

---

## 📁 ФАЙЛОВЕ В ПАКЕТА

### Core Files (Direct Replace):
```
db.py                          → app/db.py
crud.py                        → app/crud.py
practice.py                    → app/routers/practice.py
home.html                      → app/templates/home.html
admin_index.html               → app/templates/admin/index.html
```

### New Templates:
```
phrases.html                   → app/templates/practice/phrases.html
phrases_admin.html             → app/templates/admin/phrases.html
edit_noun.html                 → app/templates/admin/edit_noun.html
edit_verb.html                 → app/templates/admin/edit_verb.html
edit_adjective.html            → app/templates/admin/edit_adjective.html
edit_phrase.html               → app/templates/admin/edit_phrase.html
```

### Code Snippets (for manual updates):
```
admin_edit_routes.py           - Edit routes за admin.py
admin_phrases_routes.py        - Phrases routes за admin.py
COMPLETE_IMPORT_FUNCTIONS.py  - Обновени import функции
```

---

## ⚡ QUICK START (Fast Deploy)

### 1. Backup
```bash
cd ~/Documents
cp -r norsk-drill norsk-drill-backup-$(date +%Y%m%d)
```

### 2. Copy Files
```bash
cd ~/Documents/norsk-drill

# Core files
cp db.py app/db.py
cp crud.py app/crud.py
cp practice.py app/routers/practice.py
cp home.html app/templates/home.html
cp admin_index.html app/templates/admin/index.html

# Templates
cp phrases.html app/templates/practice/
cp phrases_admin.html app/templates/admin/phrases.html
cp edit_*.html app/templates/admin/
```

### 3. Update admin.py
```bash
# Manual edit required!
# See admin_py_changes.md for details
nano app/routers/admin.py
```

### 4. Add Edit Buttons
```bash
# Manual edit required!
# Edit these files:
# - app/templates/admin/nouns.html
# - app/templates/admin/verbs.html
# - app/templates/admin/adjectives.html
```

### 5. Deploy
```bash
git add .
git commit -m "Major update v2.0"
git push

# On Pi:
sudo systemctl stop norsk-drill && git pull && sudo systemctl start norsk-drill
```

---

## 🎯 КАКВО Е НОВО?

### 1. Validation Fix
**Преди:** Празни полета → ✅ Correct  
**След:** Празни полета → ❌ Incorrect  

### 2. Parentheses Ignore
**Преди:** "време" ≠ "време (навън)"  
**След:** "време" = "време (навън)" ✅  

### 3. Duplicate Checking
**Преди:** CSV import 2x → 2x думи в база  
**След:** CSV import 2x → 1x думи (skip duplicates)  

### 4. Edit Functionality
**Ново:** ✏️ Edit бутон до всяка дума в Admin  
- Промяна на форми
- Поправяне на преводи
- Обновяване на групи

### 5. Phrases (NEW!)
**Ново:** 🗣️ Phrases категория  
- Фрази и изрази
- Category organization
- Notes field
- Practice като други категории

---

## 🗄️ DATABASE CHANGES

**Нови колони:**
- `verbs.group`
- `verbs.group_description`
- `adjectives.group`
- `adjectives.group_description`

**Нова таблица:**
- `phrases` (norwegian, translations, category, notes)

**Миграция:** Автоматична при първо стартиране!

---

## ✅ TESTING CHECKLIST

След deploy, тествай:

- [ ] Practice Verbs - празни полета = грешно
- [ ] Translation с "(текст)" - работи без скобите
- [ ] Import същ CSV 2x - само 1x в база
- [ ] Edit бутон в Admin - работи
- [ ] Phrases практика - показва се
- [ ] Phrases admin - работи import/edit/delete

---

## 📞 SUPPORT FILES

- `DEPLOYMENT_GUIDE.md` - Пълен deployment guide
- `FILE_MAPPING.md` - File-by-file mapping
- `admin_py_changes.md` - Admin.py промени
- `COMPLETE_IMPORT_FUNCTIONS.py` - Import функции reference

---

## 🎉 РЕЗУЛТАТ

След deploy ще имаш:

✨ **По-строга валидация**  
✨ **По-smart проверка на преводи**  
✨ **Защита от дубликати**  
✨ **Пълен контрол с Edit**  
✨ **Нова Phrases категория**  

---

## 📈 VERSION INFO

**Version:** 2.0  
**Release Date:** 2025-12-17  
**Files Changed:** 16  
**New Features:** 5  
**Breaking Changes:** None (backward compatible)  

---

## ⚠️ ВАЖНИ ЗАБЕЛЕЖКИ

1. **Backup преди deploy!**
2. **Database ще се обнови автоматично**
3. **Съществуващи данни ще останат**
4. **Ръчно редактиране на admin.py е задължително**
5. **Тествай локално преди Pi deploy**

---

## 🚀 READY?

**Следвай DEPLOYMENT_GUIDE.md за стъпка-по-стъпка инструкции!**

**Успех с deploy-а!** 💪

---

**Made with ❤️ for Norwegian language learning** 🇳🇴
