# PRODUCT REQUIREMENTS DOCUMENT

# AI-POWERED WEBSITE SERVICE — WEBIA

**(Web Business & Intelligent Automation)**
*Website Pintar untuk Bisnis*

**PRD v1.0 | Formal Product & Engineering Specification**
**Status:** Baseline / Development Reference
**Tanggal:** 7 Oktober 2026

> **CORE PRINCIPLE**
>
> **PUBLIC WEBSITE ALWAYS.**
> **AI ALWAYS.**
> **LOGIN WHEN NEEDED.**
> **MODULES WHEN NEEDED.**
> **SCALE WITHOUT REBUILDING.**

---

## 1. Document Control

| Item | Detail |
|---|---|
| Document | Product Requirements Document (PRD) |
| Product | AI-Powered Website Service |
| Version | 1.0 |
| Status | Baseline / Development Reference |
| Primary Purpose | Menjadi acuan bisnis, product, design, frontend, backend, AI, QA, dan deployment. |
| Target Users | UMKM, bisnis lokal, perusahaan, agency, professional service, creator, retail, education, healthcare, property, automotive, F&B, beauty, dan kategori bisnis lain. |
| Core Differentiator | Setiap website customer selalu dilengkapi AI Business Chatbot yang memahami konteks bisnis customer. |

---

## 2. Executive Summary

AI-Powered Website Service adalah layanan pembuatan website bisnis yang menggabungkan public website, reusable template, paket layanan bertingkat, modul bisnis yang dapat ditambahkan sesuai kebutuhan, dan AI Business Chatbot.

Produk utama perusahaan bukan sekadar jasa membuat halaman web. Sistem dirancang sebagai platform produksi website yang modular dan scalable sehingga satu arsitektur dapat melayani banyak kategori bisnis tanpa harus membangun sistem dari nol.

Semua website customer memiliki AI Business Chatbot sebagai fitur inti. Perbedaan antar paket terletak pada kompleksitas website, level SEO, kemampuan pengelolaan konten, admin dashboard, dan business modules.

Authentication tidak diwajibkan untuk semua website; login hanya digunakan jika memang dibutuhkan oleh paket, modul, atau model bisnis customer.

---

## 3. Product Vision & Goals

### 3.1 Product Vision

Membangun layanan website bisnis modern yang dapat diproduksi secara cepat, konsisten, scalable, mudah dikustomisasi, dan memiliki AI sebagai lapisan interaksi bisnis.

### 3.2 Product Goals

- Menyediakan website bisnis yang siap digunakan oleh berbagai kategori industri.
- Menyediakan template reusable untuk mempercepat development dan menjaga konsistensi kualitas.
- Menjadikan AI Business Chatbot sebagai fitur standar pada seluruh paket.
- Menyediakan 5 paket produk dengan tingkat kemampuan yang jelas dan mudah dipahami customer.
- Memisahkan kebutuhan public website, admin, member, dan business modules agar tidak semua customer dipaksa menggunakan login.
- Menyimpan data customer, order, project, dan konfigurasi website secara terstruktur di database internal perusahaan.
- Menerapkan multi-tenant architecture agar data dan knowledge AI setiap customer terisolasi.
- Menyediakan jalur upselling dari website sederhana sampai custom business platform.
- Memungkinkan penambahan kategori, template, paket, modul, dan fitur tanpa mengubah core architecture.

---

## 4. Product Scope

### 4.1 In Scope

- Company main website sebagai sales/marketing storefront.
- Category, template, package, module/add-on, portfolio, FAQ, contact, pricing, dan order flow.
- AI Sales Assistant pada website perusahaan.
- AI Business Chatbot pada setiap customer website.
- Customer data, business brief, website configuration, AI knowledge, order, dan project management.
- Public customer website.
- Conditional authentication untuk admin/member.
- Reusable template architecture.
- Multi-tenant data dan AI knowledge isolation.
- SEO level berdasarkan paket.
- WhatsApp CTA dan human handoff.
- MVP hingga fase pengembangan lanjutan.

### 4.2 Out of Scope for MVP

- Advanced CRM.
- Full e-commerce.
- Advanced booking engine.
- Payment gateway penuh.
- Membership/loyalty kompleks.
- Voice AI.
- AI image generation.
- ERP integration.
- Automated website generation end-to-end.
- Advanced analytics.

---

## 5. Product Principles

| Principle | Definition |
|---|---|
| Public Website Always | Setiap customer website minimal memiliki public website yang dapat diakses visitor. |
| AI Always | Setiap paket customer website memiliki AI Business Chatbot. |
| Login When Needed | Authentication hanya diterapkan bila dibutuhkan oleh admin, member, portal, course, loyalty, atau kebutuhan bisnis lain. |
| Modules When Needed | Booking, payment, e-commerce, CRM, member area, dan fitur lain bersifat modular. |
| Scale Without Rebuilding | Kategori dan kebutuhan baru harus dapat ditambahkan melalui konfigurasi/modul, bukan membuat arsitektur baru. |
| Template First | Template reusable menjadi accelerator produksi, bukan website one-off yang selalu dibuat dari nol. |
| Tenant Isolation | Data bisnis dan AI knowledge customer tidak boleh tercampur dengan tenant lain. |
| Controlled AI | AI hanya boleh menjawab berdasarkan knowledge yang tersedia dan harus melakukan fallback bila tidak mengetahui jawaban. |

---

## 6. Target Market & Category System

Kategori harus bersifat extensible. Kategori awal meliputi:

| Category | Group Examples |
|---|---|
| F&B | Restaurant, Cafe, Catering, Bakery, Food Product |
| Beauty | Salon, Barbershop, Beauty Clinic, Skincare, Makeup Artist |
| Automotive | Bengkel, Car Wash, Dealer, Body Repair |
| Company | Company Profile, Contractor, Distributor, Manufacturer, Agency |
| Property | Developer, Property Agent, Real Estate, Villa |
| Education | School, Course, Tutor, Training, Online Course |
| Professional Service | Consultant, Lawyer, Accountant, Freelancer |
| Personal Brand | Creator, Influencer, Portfolio |
| Retail | Store, Distributor, Supplier |
| Healthcare | Clinic, Pharmacy, Medical Practice |

Kategori baru dapat ditambahkan tanpa mengubah core architecture selama mengikuti model **category-template-package-module**.

### 6.1 Category Catalog

Category bukan hanya filter tampilan pada website utama. Category merupakan dasar untuk menentukan template, recommendation package, contoh portfolio, module yang relevan, dan business knowledge structure. Arsitektur category harus extensible sehingga kategori baru dapat ditambahkan tanpa perubahan core architecture.

### 6.2 Initial Category Catalog

| Category Group | Subcategories / Business Types | Typical Website Needs |
|---|---|---|
| F&B | Restaurant; Cafe; Catering; Bakery; Food Product; Catering Kantor; Coffee Shop; Dessert Shop; Food Stall | Menu, product/service, location, opening hours, reservation/booking, WhatsApp, promo, AI FAQ |
| Beauty | Salon; Barbershop; Beauty Clinic; Skincare; Makeup Artist; Nail Salon; Spa | Service, price, duration, booking, stylist/therapist, promo, location, AI recommendation |
| Automotive | Bengkel; Car Wash; Dealer; Body Repair; Detailing; Tire & Service; Auto Accessories | Service, price, booking, vehicle/service type, location, WhatsApp, AI FAQ |
| Company | Company Profile; Contractor; Distributor; Manufacturer; Agency; Supplier; Trading; Construction | About, services, portfolio, projects, certifications, clients, contact, quotation lead, AI company FAQ |
| Property | Developer; Property Agent; Real Estate; Villa; Apartment; Kost; Housing; Commercial Property | Property listing, gallery, location, specification, price, inquiry, booking/viewing, AI property FAQ |
| Education | School; Course; Tutor; Training; Bootcamp; Learning Center; Online Course; Workshop | Programs, schedules, teachers, pricing, registration, course content, member area, AI FAQ |
| Professional Service | Consultant; Lawyer; Accountant; Tax Consultant; Architect; Freelancer; Notary; Business Service | Services, expertise, pricing/consultation, portfolio, appointment, lead form, AI consultation FAQ |
| Personal Brand | Creator; Influencer; Portfolio; Public Speaker; Artist; Photographer; Coach | Profile, portfolio, services, media kit, collaboration form, social links, AI profile/FAQ |
| Retail | Store; Distributor; Supplier; Wholesale; Fashion; Electronics; Furniture; General Retail | Product catalog, price, stock/availability, inquiry, WhatsApp, optional e-commerce, AI product FAQ |
| Healthcare | Clinic; Pharmacy; Medical Practice; Dental Clinic; Laboratory; Wellness Center | Services, doctor/staff, schedule, location, appointment, FAQ, policy, AI information assistant |

### 6.3 Category-to-Product Logic

- Category menentukan daftar template yang direkomendasikan.
- Category dapat memengaruhi rekomendasi package oleh AI Sales Assistant.
- Category dapat memengaruhi module recommendation, misalnya Salon → Booking; Online Course → Member; Retail → E-commerce.
- Category menentukan contoh content structure, seperti Menu untuk F&B, Service untuk Beauty/Automotive, Property Listing untuk Property, dan Course untuk Education.
- Category tidak boleh mengunci sistem ke satu workflow. Business requirement tetap menjadi penentu akhir.
- Satu customer dapat memiliki satu primary category dan, bila diperlukan, secondary category.
- Template dapat digunakan oleh lebih dari satu category apabila struktur dan desainnya compatible.

### 6.4 Category → Template → Package → Module

Hubungan product catalog menggunakan konsep *recommendation*, bukan *hard-coded restriction*. Contoh berikut menunjukkan bagaimana category menjadi starting point:

| Business Example | Recommended Template | Recommended Package | Typical Modules |
|---|---|---|---|
| Cafe | F01 Modern Restaurant / F02 Premium Cafe | Starter / Business | Menu, WhatsApp, Booking optional, AI |
| Salon | B01 Elegant Salon / B02 Luxury Beauty | Business / Professional | Booking, Admin, Service Management, AI |
| Bengkel | A01 Professional Workshop | Starter / Business / Professional | Service, Booking, WhatsApp, Admin optional, AI |
| Contractor | C01 Corporate Contractor | Business / Professional / Custom | Portfolio, Project, Lead Form, SEO, AI |
| Property | P01 Property Showcase | Business / Professional / Custom | Property Listing, Inquiry, Booking, AI |
| Online Course | E01 Learning Platform | Professional / Custom | Member, Course, Payment, Admin, AI |
| Clinic | H01 Professional Clinic | Business / Professional / Custom | Doctor/Service, Appointment, FAQ, AI |
| Retail | R01 Modern Store | Business / Professional / Custom | Product, E-commerce, Payment, AI |
| Creator | PB01 Creator Portfolio | Starter / Business | Portfolio, Media Kit, Collaboration Form, AI |

### 6.5 Category Expansion Rules

- Penambahan kategori baru tidak boleh membutuhkan perubahan besar pada database core.
- Setiap kategori baru minimal memiliki business type, description, recommended templates, recommended modules, dan AI knowledge fields.
- Category catalog harus dapat dikelola oleh Internal Company Admin.
- Template dapat diberi satu atau beberapa tag category.
- Module compatibility harus dapat dikonfigurasi.
- AI Sales Assistant menggunakan category catalog sebagai salah satu sumber recommendation.
- Jika kebutuhan customer tidak cocok dengan kategori yang tersedia, customer dapat diarahkan ke Custom package.

---

## 7. Package Structure

Produk memiliki 5 paket. AI Business Chatbot merupakan fitur **wajib** pada seluruh paket. SEO menjadi salah satu pembeda antar paket.

| Paket | Positioning | Scope | AI | SEO | Admin | Target |
|---|---|---|---|---|---|---|
| STATIC | Landing Page Statis | Landing page sederhana dengan konten relatif fixed. | Wajib | Basic/Technical | Tidak | Bisnis kecil yang hanya membutuhkan online presence. |
| STARTER | AI Landing Page | Landing page bisnis dengan struktur lebih siap untuk pengembangan. | Wajib | Basic SEO | Tidak | UMKM/bisnis yang ingin website + AI. |
| BUSINESS | AI Business Website | Website bisnis lengkap dengan beberapa halaman/section. | Wajib | Standard SEO | Opsional | Bisnis yang membutuhkan company/product/service presence. |
| PROFESSIONAL | AI Website + Admin | Website lengkap dengan admin dashboard dan content management. | Wajib | Advanced SEO | Ya | Bisnis yang ingin mengelola website sendiri. |
| CUSTOM | AI Custom Business Platform | Website dan sistem sesuai workflow bisnis customer. | Wajib | Advanced/Custom SEO | Ya | Perusahaan/kebutuhan kompleks. |

### 7.1 Paket 1 — STATIC

- Landing page statis.
- Responsive design.
- Business profile.
- About.
- Product/service information.
- Gallery sederhana.
- Contact.
- WhatsApp CTA.
- Google Maps bila diperlukan.
- Performance/asset optimization dasar.
- AI Business Chatbot wajib.
- Tidak menyediakan admin dashboard secara default.
- Tidak menyediakan member login.
- Konten umumnya dikelola melalui proses layanan perusahaan.

> **Catatan:** istilah "static" mengacu pada struktur/content website, bukan berarti AI chatbot tidak dapat berjalan. AI dapat tetap menggunakan backend/service AI tersendiri.

### 7.2 Paket 2 — STARTER

- Landing page bisnis.
- Responsive.
- Business information.
- Product/service.
- Contact dan WhatsApp.
- Google Maps/social media integration.
- Basic SEO.
- AI Business Chatbot.
- FAQ/CTA dasar.
- Tidak ada admin dashboard secara default.

### 7.3 Paket 3 — BUSINESS

- Multi-section/multi-page website.
- About, product, service, gallery, testimonial, FAQ, contact.
- WhatsApp CTA.
- Google Maps.
- Standard SEO.
- Analytics dasar bila termasuk konfigurasi.
- AI Business Chatbot.
- Optional business modules.
- Authentication optional sesuai modul.

### 7.4 Paket 4 — PROFESSIONAL

- Semua fitur BUSINESS.
- Admin Login.
- Admin Dashboard.
- Product Management.
- Service Management.
- Gallery Management.
- FAQ Management.
- Testimonial Management.
- Content Management.
- AI Knowledge Management.
- Advanced SEO.
- Leads/booking bila modul dipilih.
- Role and permission sesuai kebutuhan.

### 7.5 Paket 5 — CUSTOM

- Custom UI/UX.
- Custom business workflow.
- E-commerce.
- Booking.
- Membership.
- Customer Portal.
- Payment Gateway.
- CRM.
- ERP integration.
- API integration.
- WhatsApp API.
- Advanced AI.
- Advanced/Custom SEO.
- Custom dashboard.
- Multi-role user.
- Custom automation.

### 7.6 Category & Package Recommendation Matrix

Package recommendation bersifat dinamis. Tabel berikut menjadi baseline recommendation, bukan pembatas teknis. Customer tetap dapat meminta custom scope.

| Category | Typical Entry Package | When to Upgrade |
|---|---|---|
| F&B | Static / Starter / Business | Professional jika perlu admin; Custom untuk ordering/e-commerce kompleks |
| Beauty | Starter / Business | Professional untuk admin + booking; Custom untuk membership/loyalty kompleks |
| Automotive | Starter / Business | Professional untuk service management; Custom untuk booking/workshop workflow kompleks |
| Company | Business / Professional | Custom untuk portal, CRM, ERP, integrations |
| Property | Business / Professional | Custom untuk listing engine, payment, portal, CRM |
| Education | Business / Professional | Custom untuk LMS, payment, member, progress, certificate |
| Professional Service | Starter / Business | Professional untuk lead/content management; Custom untuk client portal |
| Personal Brand | Static / Starter / Business | Professional bila perlu CMS/content management |
| Retail | Business / Professional | Custom untuk e-commerce, payment, inventory integration |
| Healthcare | Business / Professional | Custom untuk appointment, portal, integrations, compliance requirements |

---

## 8. SEO Strategy

SEO merupakan capability bertingkat, bukan pengganti AI. Semua paket tetap memiliki AI Business Chatbot.

| Paket | SEO Level | Contoh Capability |
|---|---|---|
| Static | Basic/Technical | Responsive, semantic structure, metadata dasar, optimized assets, basic indexing readiness. |
| Starter | Basic SEO | Meta title/description, heading structure, sitemap/robots bila applicable, basic local SEO readiness. |
| Business | Standard SEO | Semua Basic + structured content, internal linking, richer metadata, analytics/Search Console readiness. |
| Professional | Advanced SEO | Semua Standard + content management, blog/landing optimization, schema strategy, technical SEO support. |
| Custom | Advanced/Custom | SEO disesuaikan dengan business goals, architecture, content strategy, integrations, dan technical requirements. |

SEO deliverables dapat disesuaikan berdasarkan scope kontrak. Tidak semua fitur SEO otomatis berarti ranking/traffic dijamin.

---

## 9. Module / Add-On System

| Module | Purpose | Authentication |
|---|---|---|
| Landing Page | Public website | Tidak |
| AI Chatbot | AI customer-facing assistant | Tidak |
| WhatsApp CTA | Contact/handoff | Tidak |
| Contact Form | Lead/contact collection | Tidak |
| Booking | Appointment/reservation | Opsional |
| Admin Dashboard | Website management | Admin auth |
| Product Management | CRUD products | Admin auth |
| Service Management | CRUD services | Admin auth |
| Member Area | Membership/course/portal | Member auth |
| E-commerce | Catalog/cart/order | Opsional |
| Payment | Payment processing | Opsional |
| CRM | Lead/customer management | Admin auth |
| Customer Portal | Customer-specific portal | Customer auth |
| Blog | Content/SEO | Opsional |
| Analytics | Business/website analytics | Opsional |
| Advanced AI | Advanced workflows/RAG/automation | AI service |
| WhatsApp API | Automated messaging | Integration |

---

## 10. Authentication & Access Model

Authentication bukan requirement universal. Sistem harus menentukan authentication berdasarkan kombinasi **category + package + module + business requirement**.

| Role | Purpose | Login |
|---|---|---|
| Public Visitor | Mengakses public website | Tidak |
| Buyer | Mengisi order/brief pada company website | Tidak wajib; data tetap disimpan |
| Customer Admin | Mengelola website customer | Ya, jika Admin module tersedia |
| Member | Mengakses member/course/loyalty/portal | Ya, jika Member module tersedia |
| Internal Company Admin | Mengelola customer/order/project/product catalog perusahaan | Ya |

**Prinsip penting:** Buyer Account ≠ Website User Account. Buyer dapat tercatat di database perusahaan tanpa memiliki akun login pada website customer.

---

## 11. AI Architecture

### 11.1 AI Layer #1 — Sales AI Assistant

- Berada di website utama perusahaan.
- Menjelaskan paket, template, kategori, modul, FAQ, dan proses order.
- Merekomendasikan paket berdasarkan kebutuhan prospect.
- Merekomendasikan template/category.
- Membantu membuat business brief.
- Mengarahkan ke demo/order/human support.
- Menggunakan controlled company knowledge.
- Tidak boleh mengarang harga, fitur, SLA, atau kebijakan yang tidak tersedia.

### 11.2 AI Layer #2 — Business AI Chatbot

- Berada pada setiap customer website.
- Memahami business-specific knowledge.
- Menjawab pertanyaan produk, layanan, harga, jam buka, lokasi, promo, kebijakan, dan FAQ.
- Merekomendasikan produk/service berdasarkan knowledge.
- Mengumpulkan lead/contact jika modul tersedia.
- Mengarahkan visitor ke WhatsApp/human support.
- Mendukung booking bila booking module tersedia.
- Melakukan fallback jika informasi tidak ditemukan.

### 11.3 AI Knowledge Structure

| Knowledge Type | Example Data |
|---|---|
| Business | Nama, deskripsi, alamat, jam operasional, kontak |
| Product | Nama, deskripsi, harga, kategori, availability |
| Service | Nama, deskripsi, harga, durasi |
| FAQ | Question, answer |
| Promotion | Nama, periode, syarat |
| Policy | Booking, payment, refund, delivery |
| CTA | WhatsApp, phone, form, booking |

### 11.4 Multi-Tenant AI Isolation

Setiap customer dianggap sebagai tenant terpisah. Retrieval, context, knowledge base, permissions, dan AI responses harus dibatasi berdasarkan `tenant_id` / `customer_id`.

- Tenant A hanya dapat mengambil knowledge Tenant A.
- Tenant B hanya dapat mengambil knowledge Tenant B.
- Prompt/context tidak boleh mencampurkan data tenant.
- Vector database/retrieval metadata harus memiliki tenant boundary.
- Admin Customer A tidak boleh mengakses data Customer B.
- AI Customer A tidak boleh menjawab berdasarkan informasi Customer B.

### 11.5 AI Fallback & Human Handoff

- Jika knowledge tidak tersedia, AI tidak boleh mengarang.
- AI menyatakan bahwa informasi belum tersedia atau meminta klarifikasi.
- Jika sesuai konfigurasi, AI menawarkan WhatsApp/human support.
- Fallback event dapat dicatat untuk evaluasi dan peningkatan knowledge.

---

## 12. Main Company Website

Website utama berfungsi sebagai sales storefront dan order platform.

- Home / Hero.
- Category Explorer.
- Template Gallery.
- Package Comparison.
- Module/Add-On Catalog.
- Portfolio/Demo.
- How It Works.
- FAQ.
- Pricing.
- Contact.
- AI Sales Assistant.
- Checkout/Order.

### 12.1 Category Explorer

- Creator/Influencer.
- Brand.
- Product.
- F&B.
- Beauty.
- Automotive.
- Company.
- Property.
- Education.
- Professional Service.
- Retail.
- Healthcare.
- Kategori dapat ditambah di masa depan.

---

## 13. Checkout & Customer Data

### 13.1 Buyer Data

- Name
- Email
- Phone/WhatsApp
- Address

### 13.2 Business Data

- Business name
- Category
- Business description
- Business address
- Contact
- Social media
- Operating hours

### 13.3 Website Configuration

- Selected category
- Template
- Package
- Modules/add-ons
- Domain preference
- Language
- Branding
- Pages/sections

### 13.4 AI Configuration

- Products
- Services
- Prices
- FAQ
- Business information
- Promotions
- Policies
- CTA
- Other approved business knowledge

### 13.5 Order Flow

1. Visitor opens company main website.
2. Visitor chooses category.
3. Visitor previews/selects template.
4. Visitor selects package.
5. Visitor selects modules/add-ons.
6. Visitor fills buyer data.
7. Visitor fills business brief.
8. Visitor configures website and AI information.
9. System displays order summary.
10. Customer proceeds to payment according to available payment method.
11. System creates Order.
12. System creates Project.
13. Project enters production workflow.

---

## 14. Project Production Workflow

```
NEW ORDER → BRIEF RECEIVED → ANALYSIS → DESIGN → FRONTEND DEVELOPMENT →
BACKEND DEVELOPMENT → AI DEVELOPMENT → INTEGRATION → QA → CLIENT REVIEW →
REVISION → APPROVAL → DEPLOYMENT → COMPLETED
```

### 14.1 Project Status Requirements

- Setiap project memiliki customer, order, package, template, modules, PIC, deadline, status, dan revision tracking.
- Status harus dapat dipantau internal company admin.
- Deadline dan PIC dapat ditentukan berdasarkan project scope.
- Deployment hanya dilakukan setelah QA dan approval sesuai SOP.

---

## 15. Reference Customer Website Scenarios

| Business | Recommended Scope | Auth |
|---|---|---|
| Cafe | Landing + Menu + Location + Hours + AI + WhatsApp | Tidak perlu login |
| Bengkel | Landing + Services + Price + AI + Booking + WhatsApp | Member login tidak wajib |
| Salon | Public + AI + Booking + Admin | Admin login |
| Online Course | Public + AI + Course + Payment + Member + Admin | Admin + Member login |
| Company Profile | Public + About + Services + Portfolio + AI + Contact | Umumnya tanpa login |

---

## 16. Functional Requirements

| ID | Requirement | Description |
|---|---|---|
| FR-001 | Category | System menampilkan daftar kategori dan memungkinkan kategori baru ditambahkan. |
| FR-002 | Template | System menampilkan template berdasarkan kategori. |
| FR-003 | Package | System menampilkan 5 paket: Static, Starter, Business, Professional, Custom. |
| FR-004 | Module | System menampilkan add-on/module yang dapat dipilih sesuai compatibility. |
| FR-005 | Template Preview | Visitor dapat melihat preview/demo template. |
| FR-006 | Package Selection | Visitor dapat memilih paket. |
| FR-007 | Module Selection | Visitor dapat memilih modul yang tersedia. |
| FR-008 | Customer Data | System meminta data buyer sebelum order. |
| FR-009 | Business Data | System meminta business brief. |
| FR-010 | Website Configuration | System menyimpan konfigurasi website. |
| FR-011 | Order Creation | System membuat order setelah checkout. |
| FR-012 | Project Creation | System membuat project berdasarkan order. |
| FR-013 | Public Website | Website tanpa auth dapat diakses tanpa login. |
| FR-014 | Admin Authentication | Admin login tersedia jika Admin module aktif. |
| FR-015 | Member Authentication | Member login tersedia jika Member module aktif. |
| FR-016 | Sales AI | AI Sales Assistant menjawab menggunakan company knowledge. |
| FR-017 | Business AI | AI Business Chatbot menjawab menggunakan customer knowledge. |
| FR-018 | AI Isolation | AI knowledge dibatasi per tenant. |
| FR-019 | Human Handoff | AI menyediakan fallback/handoff jika informasi tidak tersedia. |
| FR-020 | AI Knowledge Management | Admin customer dapat mengelola knowledge jika modul tersedia. |
| FR-021 | SEO Configuration | System menerapkan SEO level sesuai paket. |
| FR-022 | Responsive UI | Public website dan dashboard menyesuaikan device. |
| FR-023 | Access Control | System menerapkan authorization berdasarkan role dan tenant. |

---

## 17. Non-Functional Requirements

| ID | Area | Requirement |
|---|---|---|
| NFR-001 | Performance | Page loading dan API harus dioptimalkan; asset compression/caching diterapkan sesuai kebutuhan. |
| NFR-002 | Responsive | UI mendukung mobile, tablet, dan desktop. |
| NFR-003 | Security | Authentication aman, password hashing, session/security controls, API protection. |
| NFR-004 | Authorization | Role dan tenant isolation wajib diterapkan. |
| NFR-005 | Scalability | Kategori, template, package, module, customer, dan AI knowledge dapat bertambah. |
| NFR-006 | AI Latency | Response AI harus berada pada latency yang wajar sesuai provider/model. |
| NFR-007 | AI Reliability | AI harus memiliki fallback dan tidak boleh mengarang business facts. |
| NFR-008 | Maintainability | Komponen reusable dan separation of concerns. |
| NFR-009 | Observability | Error, AI fallback, usage, dan critical events dapat dilacak. |
| NFR-010 | Data Isolation | Tidak ada cross-tenant data exposure. |

---

## 18. User Roles & Responsibilities

| Role | Responsibilities |
|---|---|
| Public Visitor | Melihat website, menggunakan AI, memilih package/template/module, mengisi order. |
| Buyer/Customer | Memberikan data bisnis, melakukan order, review project. |
| Customer Admin | Mengelola website jika Admin module aktif. |
| Customer Member | Menggunakan member area jika modul aktif. |
| Internal Company Admin | Mengelola customer, order, project, catalog, assignment, status, QA/deployment. |
| Frontend Developer | UI, reusable templates, checkout, admin/member UI, AI chat UI, integration. |
| Backend Developer | Database, API, auth, business logic, order/project, tenant isolation. |
| AI Developer | Sales AI, Business AI, prompts, RAG, embeddings, vector DB, evaluation, fallback. |
| QA | Functional, responsive, security/access, AI quality, regression testing. |

---

## 19. Team Responsibility Matrix

| Workstream | Frontend | Backend | AI |
|---|---|---|---|
| Main Website | Primary | Support | Support |
| Reusable Template | Primary | Support | Support |
| Checkout | Primary | Primary | - |
| Customer/Business Data | Primary | Primary | - |
| Order | Support | Primary | - |
| Project | Support | Primary | - |
| Customer Admin | Primary | Primary | Support |
| Member Area | Primary | Primary | - |
| AI Chat UI | Primary | Support | Primary |
| Sales AI | Support | - | Primary |
| Business AI | Support | Support | Primary |
| AI Knowledge | Support | Primary | Primary |
| RAG/Vector DB | - | Support | Primary |
| Database | - | Primary | Support |
| Authentication | Support | Primary | Support |
| Tenant Isolation | Support | Primary | Primary |

---

## 20. High-Level Data Model

**Core relationship:**

```
Customer → Orders → Project → Website → Category / Template / Package / Modules / AI Knowledge
```

Supporting entities dapat mencakup:

- Customer
- Order
- OrderItem
- Project
- Website
- Category
- Template
- Package
- Module
- WebsiteModule
- AIKnowledge
- Product
- Service
- FAQ
- Promotion
- Policy
- AdminUser
- Member
- Lead
- Booking
- Payment
- Revision
- Deployment
- AnalyticsEvent

Tenant boundary harus tersedia pada seluruh entity yang bersifat customer-specific.

---

## 21. Admin Architecture

### 21.1 Customer Admin Dashboard

- Dashboard
- Product
- Service
- Gallery
- FAQ
- Blog
- Testimonial
- Leads
- Booking
- AI Knowledge
- User Management
- Website Settings
- SEO Settings jika tersedia

### 21.2 Internal Company Admin

- Customer Management
- Order Management
- Project Management
- Category Management
- Template Management
- Package Management
- Module Management
- PIC/Developer Assignment
- Deadline
- Revision Tracking
- QA
- Deployment
- Portfolio/Demo Management

---

## 22. Product Roadmap

### 22.1 MVP

- Company main website: landing, category, template, package, module, portfolio, FAQ, contact.
- 5 package catalog: Static, Starter, Business, Professional, Custom.
- Template preview.
- Order/checkout flow.
- Customer data and business brief.
- Backend: customer, category, template, package, module, order, project.
- Customer website public layer.
- Basic business content.
- WhatsApp CTA.
- AI Sales Assistant.
- AI Business Chatbot.
- Basic AI knowledge: business, product/service, FAQ.
- Human handoff.
- Tenant isolation foundation.
- Basic SEO according to package.

### 22.2 Phase 2

- Customer Admin Dashboard.
- Dynamic CMS.
- AI Knowledge Management.
- Booking.
- Leads.
- Member authentication.
- Customer dashboard.
- Analytics.
- WhatsApp API.
- Advanced RAG.

### 22.3 Phase 3

- E-commerce.
- Payment gateway.
- CRM.
- ERP integration.
- Subscription.
- Loyalty.
- Voice AI.
- AI automation.
- Advanced analytics.
- Automated website generation.

---

## 23. Acceptance Criteria

### 23.1 Company Website

- Visitor dapat melihat kategori, template, package, module, portfolio, FAQ, dan contact.
- Visitor dapat memilih paket dan module.
- Visitor dapat melakukan order.
- Customer data dan business brief tercatat.
- Sales AI menjawab berdasarkan company knowledge.
- AI tidak mengarang harga/fungsi yang tidak tersedia.

### 23.2 Customer Website

- Public website dapat diakses tanpa login bila tidak ada auth requirement.
- Website responsive.
- Business information sesuai brief.
- Product/service sesuai data.
- Contact dan WhatsApp tersedia.
- AI Chatbot tersedia.
- AI menjawab berdasarkan customer knowledge.
- Tidak ada cross-tenant knowledge leakage.
- AI melakukan fallback jika informasi tidak tersedia.

### 23.3 Authentication

- No-login website tetap dapat digunakan tanpa login.
- Admin module memiliki login/logout/permission yang aman.
- Member module memiliki registration/login/logout dan data member terisolasi.
- Buyer tanpa member account tetap dapat tercatat di company database.

### 23.4 AI

- AI memahami natural language.
- AI dapat menjawab FAQ/product/service.
- AI menggunakan knowledge tenant yang benar.
- AI memiliki fallback untuk unknown information.
- AI tidak melakukan business hallucination.
- AI dapat melakukan human/WhatsApp handoff sesuai konfigurasi.

---

## 24. Success Metrics & KPI

| Area | Metric | Definition |
|---|---|---|
| Business | Website Visitors | Jumlah visitor pada company website dan customer sites. |
| Business | AI Conversations | Jumlah percakapan dengan AI. |
| Business | Leads | Jumlah lead yang dihasilkan. |
| Business | Orders | Jumlah order. |
| Business | Conversion Rate | Visitor → Lead/Order. |
| Business | Average Order Value | Nilai rata-rata transaksi. |
| Business | Package Upgrade | Jumlah customer yang upgrade package. |
| Business | Add-on Purchase | Jumlah module/add-on yang dibeli. |
| Production | Average Project Duration | Rata-rata waktu pengerjaan. |
| Production | Revision Count | Jumlah revisi per project. |
| Production | On-time Delivery | Persentase project selesai sesuai deadline. |
| Production | Completion Rate | Persentase project completed. |
| AI | Answer Accuracy | Akurasi jawaban AI. |
| AI | Resolution Rate | Percakapan selesai tanpa human handoff. |
| AI | Human Handoff Rate | Persentase conversation yang perlu bantuan manusia. |
| AI | Unanswered Rate | Persentase pertanyaan yang tidak dapat dijawab. |
| AI | AI Usage | Jumlah conversation/message/token sesuai monitoring. |
| AI | Satisfaction | Feedback pengguna terhadap AI. |

---

## 25. Business Model

### 25.1 One-Time Revenue

- Website package.
- Custom development.
- Module/add-on.
- Additional pages/features.

### 25.2 Recurring Revenue

- Domain.
- Hosting.
- Maintenance.
- AI service.
- AI usage.
- Support.
- Optional SEO/content service.

### 25.3 Upsell Path

```
STATIC → STARTER → BUSINESS → PROFESSIONAL → CUSTOM
```

Upsell dilakukan berdasarkan kebutuhan customer, bukan dengan memaksa authentication. Customer dapat menambahkan module tertentu tanpa harus mengganti seluruh website apabila architecture dan package mendukungnya.

---

## 26. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| AI hallucination | AI memberikan informasi bisnis yang salah. | Controlled knowledge, retrieval, guardrails, fallback, evaluation. |
| Cross-tenant leakage | AI/data customer tercampur. | `tenant_id` enforcement, isolated retrieval metadata, authorization, testing. |
| Package confusion | Customer tidak memahami perbedaan paket. | Feature comparison, examples, AI Sales Assistant, clear package boundaries. |
| Over-customization | Development menjadi lambat karena setiap website dibuat dari nol. | Reusable templates, modules, configuration-driven architecture. |
| SEO expectation | Customer menganggap SEO menjamin ranking. | Define deliverables clearly; no ranking guarantee. |
| AI operating cost | Biaya AI meningkat seiring usage. | Usage monitoring, quotas, model selection, caching, pricing strategy. |
| Scope creep | Permintaan di luar package. | Order scope, module catalog, change request/revision policy. |
| Security | Unauthorized access. | Authentication, authorization, hashing, API security, logging, security testing. |

---

## 27. UX / UI Requirements

- Public website harus mobile-first dan responsive.
- Package comparison harus mudah dipahami dalam sekali scan.
- Customer harus dapat memahami perbedaan Static vs Starter vs Business vs Professional vs Custom.
- AI widget harus mudah ditemukan namun tidak mengganggu primary CTA.
- Checkout harus memecah form panjang menjadi step yang jelas.
- AI Chatbot pada customer website harus menggunakan branding customer.
- Admin/member interface harus memisahkan navigation berdasarkan role.
- Template preview harus menunjukkan real-world use case.
- Error state dan fallback harus jelas serta actionable.

---

## 28. High-Level Technical Architecture

Arsitektur logis yang direkomendasikan:

```
Client / Browser
        ↓
Public Website / Customer Website
        ↓
Frontend Application
        ↓
Backend API / Application Layer
        ↓
Authentication & Authorization
        ↓
Multi-Tenant Business Layer
        ↓
Database
        ↓
AI Orchestration Layer
        ↓
Knowledge / RAG Layer
        ↓
LLM Provider
        ↓
External Integrations (WhatsApp, Payment, Analytics, etc.)
```

> **Catatan implementasi:** teknologi spesifik dapat ditentukan oleh technical lead. PRD ini mendefinisikan requirement dan behavior, bukan mengunci framework tertentu.

---

## 29. Operational & Content Rules

- Informasi bisnis yang menjadi sumber jawaban AI harus berasal dari data customer yang disetujui.
- Perubahan data penting seperti harga, jam buka, promo, dan kebijakan harus memperbarui AI knowledge.
- Customer tanpa Admin Dashboard mendapatkan perubahan melalui support/internal team.
- Customer dengan Admin Dashboard dapat mengelola knowledge sesuai permission.
- Setiap project memiliki scope, revision limit, approval, dan deployment status.
- AI response harus mengikuti bahasa/brand tone yang dikonfigurasi jika fitur tersedia.

---

## 30. Extensibility Requirements

- Kategori baru dapat ditambahkan tanpa membuat schema baru yang khusus kategori.
- Template dapat dikaitkan dengan satu atau beberapa kategori.
- Package memiliki feature entitlement/configuration.
- Module memiliki compatibility rules.
- AI knowledge schema dapat berkembang tanpa memutus data lama.
- Tenant-specific configuration harus dapat diubah tanpa memengaruhi tenant lain.
- Integrasi pihak ketiga harus melalui abstraction/service layer agar mudah diganti.

---

## 31. Glossary

| Term | Definition |
|---|---|
| Public Website | Website yang dapat diakses visitor tanpa login. |
| AI Sales Assistant | AI pada website utama perusahaan untuk membantu prospect memilih layanan dan melakukan order. |
| AI Business Chatbot | AI pada website customer yang memahami bisnis customer. |
| Tenant | Satu customer/business environment yang datanya terisolasi. |
| Admin | User yang mengelola website/customer business data. |
| Member | User akhir yang memiliki akun pada website jika member module tersedia. |
| Module | Fitur tambahan yang dapat diaktifkan sesuai kebutuhan. |
| Template | Design/structure reusable untuk mempercepat pembuatan website. |
| RAG | Retrieval-Augmented Generation untuk mengambil knowledge relevan sebelum AI menghasilkan jawaban. |
| Human Handoff | Pengalihan conversation ke manusia/WhatsApp ketika AI tidak dapat menyelesaikan kebutuhan. |

---

## 32. Final Product Definition

AI-Powered Website Service adalah layanan pembuatan website bisnis yang menggabungkan public website, reusable template, modular business features, SEO bertingkat, dan AI Business Chatbot yang memahami bisnis customer.

Website sederhana dapat berupa **Landing Page + AI + WhatsApp**. Website kompleks dapat berkembang menjadi **Public Website + AI + Admin + Member + Booking + Payment + E-commerce + CRM/ERP Integration + Advanced AI**.

> **PUBLIC WEBSITE ALWAYS.**
> **AI ALWAYS.**
> **LOGIN WHEN NEEDED.**
> **MODULES WHEN NEEDED.**
> **SCALE WITHOUT REBUILDING.**

---

*AI-Powered Website Service — PRD v1.0*
