import { useMemo, useState } from 'react'
import { SHOP_URL, departments, stores } from './data'

const STATES = ['All', 'ID', 'MT', 'WA']

function Brand({ light = false }) {
  return (
    <a className="brand" href="#top" aria-label="Super 1 Foods home">
      <span className="brand-mark" aria-hidden="true">
        S1
      </span>
      <span className="brand-name" style={light ? undefined : { color: 'var(--forest)' }}>
        Super 1 Foods
        <span>Inland Northwest</span>
      </span>
    </a>
  )
}

function Header() {
  return (
    <header className="site-header">
      <div className="wrap">
        <Brand light />
        <nav className="nav" aria-label="Primary">
          <a href="#shop">Shop</a>
          <a href="#fresh">Fresh</a>
          <a href="#story">Our Story</a>
          <a href="#locations">Locations</a>
        </nav>
        <a className="btn btn-primary header-cta" href={SHOP_URL} target="_blank" rel="noreferrer">
          Order Online
        </a>
      </div>
    </header>
  )
}

function Hero() {
  return (
    <section className="hero" id="top" aria-label="Hero">
      <div className="hero-media" aria-hidden="true">
        <img
          src="/images/hero.jpg"
          alt=""
          width={2000}
          height={1500}
          fetchPriority="high"
        />
      </div>
      <div className="wrap">
        <div className="hero-content">
          <h1>Super 1 Foods</h1>
          <p>
            Fresh food for Idaho, Montana, and Washington — family-owned since
            1970, still stocking the communities that raised us.
          </p>
          <div className="hero-actions">
            <a className="btn btn-primary" href={SHOP_URL} target="_blank" rel="noreferrer">
              Shop Pickup & Delivery
            </a>
            <a className="btn btn-ghost" href="#locations">
              Find a Store
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}

function Shop() {
  return (
    <section className="section shop" id="shop">
      <div className="wrap shop-panel">
        <div className="shop-copy">
          <h2>Groceries on your schedule</h2>
          <p>
            Order from Super 1 Foods NW for same-day delivery or curbside
            pickup — often ready in as little as an hour.
          </p>
          <a className="btn btn-primary" href={SHOP_URL} target="_blank" rel="noreferrer">
            Start Shopping
          </a>
        </div>
        <div className="shop-visual">
          <img src="/images/store.jpg" alt="Grocery aisles stocked with everyday essentials" />
        </div>
      </div>
    </section>
  )
}

function Fresh() {
  return (
    <section className="section" id="fresh">
      <div className="wrap">
        <div className="section-head">
          <h2>Built around the fresh edge</h2>
          <p>
            Produce, butcher counter, and scratch bakery — the departments
            neighbors still come in for.
          </p>
        </div>
        <div className="depts">
          {departments.map((dept) => (
            <article className="dept" key={dept.title}>
              <img src={dept.image} alt="" />
              <div className="dept-body">
                <h3>{dept.title}</h3>
                <p>{dept.copy}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function Story() {
  return (
    <section className="section" id="story">
      <div className="wrap story">
        <div className="story-media">
          <img
            src="/images/community.jpg"
            alt="Fresh market produce ready for shoppers"
          />
        </div>
        <div className="story-copy">
          <h2>A McIntire family market</h2>
          <p>
            Ron and Joanne McIntire opened their first store in Hayden in 1970.
            Decades later, Super 1 Foods remains a locally grown supermarket —
            trusted for fair prices, dependable service, and real community
            roots across the Inland Northwest.
          </p>
          <p>
            From school fundraisers to food banks, we show up the same way we
            stock shelves: consistently, and close to home.
          </p>
          <div className="values">
            <div className="value">
              <span className="value-dot" aria-hidden="true" />
              <div>
                <strong>Trust & loyalty</strong>
                <span>Neighbors first, every aisle and every shift.</span>
              </div>
            </div>
            <div className="value">
              <span className="value-dot" aria-hidden="true" />
              <div>
                <strong>Integrity & dependability</strong>
                <span>Quality you can count on, day or night.</span>
              </div>
            </div>
            <div className="value">
              <span className="value-dot" aria-hidden="true" />
              <div>
                <strong>Community safety net</strong>
                <span>Supporting schools, nonprofits, and local families.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Locations() {
  const [state, setState] = useState('All')
  const filtered = useMemo(
    () => (state === 'All' ? stores : stores.filter((s) => s.state === state)),
    [state],
  )

  return (
    <section className="section locations" id="locations">
      <div className="wrap">
        <div className="section-head">
          <h2>Find your Super 1</h2>
          <p>
            Twenty-one stores across Idaho, Montana, and Washington — many open
            around the clock.
          </p>
        </div>
        <div className="loc-toolbar" role="group" aria-label="Filter by state">
          {STATES.map((s) => (
            <button
              key={s}
              type="button"
              className={`chip${state === s ? ' active' : ''}`}
              onClick={() => setState(s)}
              aria-pressed={state === s}
            >
              {s === 'All' ? 'All stores' : s}
            </button>
          ))}
        </div>
        <div className="loc-grid">
          {filtered.map((store) => (
            <article className="loc" key={`${store.name}-${store.phone}`}>
              <h3>{store.name}</h3>
              <p>
                {store.address}
                <br />
                {store.city}, {store.state} {store.zip}
              </p>
              <p>{store.hours}</p>
              <a href={`tel:${store.phone.replace(/[^\d+]/g, '')}`}>{store.phone}</a>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function CtaBand() {
  return (
    <section className="cta-band" aria-label="Shop online call to action">
      <div className="wrap">
        <h2>Need it tonight?</h2>
        <p>
          Browse weekly deals and fill your cart for Super 1 Foods NW pickup or
          delivery.
        </p>
        <a className="btn btn-primary" href={SHOP_URL} target="_blank" rel="noreferrer">
          Open the Storefront
        </a>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="wrap">
        <div className="footer-grid">
          <Brand light />
          <div className="footer-links">
            <a href={SHOP_URL} target="_blank" rel="noreferrer">
              Shop Online
            </a>
            <a href="#locations">Store Locator</a>
            <a href="#story">Our Story</a>
            <a href="https://www.super1foods.net/" target="_blank" rel="noreferrer">
              super1foods.net
            </a>
          </div>
        </div>
        <p className="footer-note">
          © {new Date().getFullYear()} Super 1 Foods. Family-owned grocery
          stores serving the Inland Northwest.
        </p>
      </div>
    </footer>
  )
}

export default function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Shop />
        <Fresh />
        <Story />
        <Locations />
        <CtaBand />
      </main>
      <Footer />
    </>
  )
}
