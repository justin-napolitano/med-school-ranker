import { appHref } from "../lib/app-routing";

type Props = {
  caveat: string;
  aamcCaveat: string;
  methodology: Array<Record<string, any>>;
};

export function AppMethodologyView({ caveat, aamcCaveat, methodology }: Props) {
  const visibleRows = methodology.slice(0, 12);

  return (
    <>
      <section className="methodology-grid">
        <article className="method-card">
          <h2>Score-screen fit</h2>
          <p>{caveat}</p>
          <p>Labels compare applicant MCAT/GPA inputs with generated school MCAT/GPA averages or bands when those fields are available.</p>
        </article>
        <article className="method-card">
          <h2>Ranking context</h2>
          <p>Rank explanations come from generated ranking summaries, drivers, source-confidence flags, and missing-data fields.</p>
          <p>Blank or provisional fields stay visible instead of becoming implied evidence.</p>
        </article>
        <article className="method-card">
          <h2>AAMC grid context</h2>
          <p>{aamcCaveat}</p>
        </article>
        <article className="method-card">
          <h2>Live scoring formulas</h2>
          <p>Your Rank is computed in the browser from selected inputs and weights. MCAT fit is clamp(1, 10, 7 + (applicant MCAT - school MCAT) / 2).</p>
          <p>GPA fit is clamp(1, 10, 7 + (applicant GPA - school GPA) / 0.08). Cost fit gives the lowest applicable positive listed cost 10 and the highest 1.</p>
          <p>Zero or negative cost values are treated as missing. If only one residency cost is listed, the scorer uses that value as a single listed cost fallback instead of scoring the missing side as zero.</p>
        </article>
        <article className="method-card">
          <h2>Default live weights</h2>
          <p>Defaults are MCAT fit 25, GPA fit 25, state/residency fit 20, cost fit 15, and generated school context 15.</p>
          <p>Balanced, Cost-aware, Academic-screen focused, Florida-first, and State-first presets only change those deterministic weights and selected state context.</p>
        </article>
        <article className="method-card">
          <h2>Live vs baseline</h2>
          <p>Your Rank is the browser-local fit rank after current filters, exclusions, inputs, and weights. Baseline Rank is the generated pipeline rank from the payload.</p>
          <p>This is not admissions probability, and it is not a school-specific acceptance probability.</p>
        </article>
        <article className="method-card">
          <h2>Missing data policy</h2>
          <p>Missing MCAT, GPA, state/OOS context, cost, or generated school context components are excluded from the live denominator and surfaced as coverage warnings.</p>
          <p>Missing values are never treated as zero in Your Score. Weighted points use a present-components-only denominator. For cost, a single positive listed cost may stand in for the missing residency side.</p>
        </article>
        <article className="method-card">
          <h2>Zero-weight policy</h2>
          <p>A component with weight 0 stays visible and is labeled Not included: weight is 0.</p>
          <p>If all weights are 0, scoring is disabled visibly instead of falling back to default weights.</p>
        </article>
        <article className="method-card">
          <h2>Scoring workspace scope</h2>
          <p>This Scoring page covers MD schools only. DO schools need a separate scoring flow because the source context and applicant-pool assumptions differ.</p>
          <p>Build My List can still show MD and DO schools; the first scoring audit table is MD-only.</p>
        </article>
        <article className="method-card">
          <h2>Rank movement</h2>
          <p>The Scoring page compares Your Rank with Baseline Rank and shows Rank movement for currently eligible MD schools.</p>
          <p>Why did this move? uses deterministic contribution data: the largest positive weighted component, the lowest weighted component, or the largest missing component.</p>
        </article>
        <article className="method-card">
          <h2>Local-state privacy</h2>
          <p>Your inputs are stored in this browser only. They are not sent to a server by this static site.</p>
          <p>Committed code and public payloads do not include private applicant MCAT or GPA values.</p>
        </article>
        <article className="method-card">
          <h2>Ownership data status</h2>
          <p>Institution ownership filtering only activates when source-backed ownership labels are populated in the payload.</p>
          <p>When labels are missing, the control stays disabled as Unknown instead of inferring public or private status from school names.</p>
        </article>
        <article className="method-card">
          <h2>Confidence fields</h2>
          <p>Data confidence and source confidence remain transparency fields on cards and profiles.</p>
          <p>They are not Build My List filters or live score components in this slice.</p>
        </article>
      </section>

      <section className="methodology-list" aria-label="Generated scoring rows">
        <div className="feed-heading">
          <div>
            <p className="eyebrow">Generated rows</p>
            <h2>Scoring inputs shown in this build</h2>
            <p>
              Open the <a href={appHref("/scoring/")}>Scoring page</a> to inspect the current browser-local score.
            </p>
          </div>
          <div className="count-block">
            <strong>{methodology.length}</strong>
            <span>rows</span>
          </div>
        </div>
        <div className="method-row-list">
          {visibleRows.map((row, index) => (
            <article className="method-row" key={`${row.display_label || row.methodology_area || "row"}-${index}`}>
              <h3>{row.display_label || row.methodology_area || "Scoring row"}</h3>
              <p>{row.notes || row.formula_reference || "Generated scoring definition."}</p>
              <span>{row.methodology_area || "Methodology"}</span>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
