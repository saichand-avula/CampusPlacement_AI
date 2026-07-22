"use client";

import { useState } from "react";
import type { WorkflowStateResponse } from "../lib/api";

interface FormFieldItem {
  label: string;
  field_type: string;
  required: boolean;
  options: string[];
}

interface WorkflowStatePanelProps {
  state: WorkflowStateResponse;
}

function Badge({ children, color = "indigo" }: { children: React.ReactNode; color?: string }) {
  const colors: Record<string, string> = {
    indigo: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
    emerald: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    amber: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    sky: "bg-sky-500/15 text-sky-300 border-sky-500/30",
    rose: "bg-rose-500/15 text-rose-300 border-rose-500/30",
    violet: "bg-violet-500/15 text-violet-300 border-violet-500/30",
    zinc: "bg-zinc-700/40 text-zinc-400 border-zinc-600/30",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border ${colors[color] || colors.indigo}`}>
      {children}
    </span>
  );
}

/** Always rendered — shows "—" (em-dash) when value is blank/null/undefined */
function InfoRow({ label, value }: { label: string; value?: string | null }) {
  const display = value && value.trim() ? value : "—";
  const isEmpty = display === "—";
  return (
    <div className="flex items-start gap-2 py-1.5 border-b border-zinc-800/50 last:border-0">
      <span className="text-[11px] text-zinc-500 w-32 flex-shrink-0 pt-0.5">{label}</span>
      <span className={`text-[12px] flex-1 break-words ${isEmpty ? "text-zinc-600 italic" : "text-zinc-200"}`}>
        {display}
      </span>
    </div>
  );
}

/** Section divider */
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 pt-3 pb-1.5">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">{children}</span>
      <div className="flex-1 h-px bg-zinc-800/80" />
    </div>
  );
}

function LinkButton({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800/80 hover:bg-zinc-700/80
        border border-zinc-700/50 hover:border-zinc-600/70 text-zinc-200 text-xs font-medium
        transition-all duration-150 active:scale-95 group"
    >
      <span className="text-indigo-400 group-hover:text-indigo-300 transition-colors">{icon}</span>
      {label}
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        className="w-3 h-3 ml-auto text-zinc-500 group-hover:text-zinc-400">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
        <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
      </svg>
    </a>
  );
}

const FIELD_TYPE_ICONS: Record<string, string> = {
  short_text: "Aa",
  paragraph: "¶",
  email: "@",
  number: "#",
  phone: "☎",
  date: "📅",
  dropdown: "▾",
  multiple_choice: "◉",
  checkboxes: "☑",
};

export default function WorkflowStatePanel({ state }: WorkflowStatePanelProps) {
  const [expanded, setExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "form" | "links">("overview");

  const eoi = state.eoi_fields;
  const hasFormLink = !!state.form_link;

  return (
    <div className={`
      workflow-panel relative overflow-hidden
      bg-gradient-to-br from-zinc-900/95 via-zinc-900 to-zinc-950
      border border-zinc-700/50 rounded-xl shadow-2xl
      transition-all duration-300
    `}>
      {/* Glowing accent line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-600 opacity-80" />

      {/* ─── Header ─────────────────────────────── */}
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-500/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              className="w-3.5 h-3.5 text-indigo-400">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Workflow Output</h3>
            <p className="text-[10px] text-zinc-500">Placement drive initialized</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge color="emerald">✓ Active</Badge>
          <button
            id="workflow-panel-toggle"
            onClick={() => setExpanded(!expanded)}
            className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              className={`w-4 h-4 transition-transform duration-200 ${expanded ? "" : "rotate-180"}`}>
              <polyline points="18 15 12 9 6 15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Company + quick summary */}
      {eoi && (
        <div className="px-4 pb-3 flex items-center gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-base font-bold text-zinc-100 truncate">{eoi.company_name}</p>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {eoi.employment_type && <Badge color="sky">{eoi.employment_type}</Badge>}
              {eoi.work_location && <Badge color="violet">{eoi.work_location}</Badge>}
              {eoi.job_designation?.slice(0, 2).map((t) => (
                <Badge key={t} color="indigo">{t}</Badge>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─── Expandable body ─────────────────────── */}
      {expanded && (
        <>
          {/* Tab bar */}
          <div className="flex border-t border-b border-zinc-800/70 px-1">
            {(["overview", "form", "links"] as const).map((tab) => (
              <button
                key={tab}
                id={`workflow-tab-${tab}`}
                onClick={() => setActiveTab(tab)}
                className={`
                  flex-1 py-2 text-[11px] font-semibold uppercase tracking-wide
                  transition-colors duration-150
                  ${activeTab === tab
                    ? "text-indigo-400 border-b-2 border-indigo-500"
                    : "text-zinc-500 hover:text-zinc-300"
                  }
                `}
              >
                {tab === "overview" ? "Job Details" : tab === "form" ? "Form Fields" : "Links"}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="px-4 py-3 max-h-[480px] overflow-y-auto scrollbar-thin">

            {/* ─ Overview tab ─ */}
            {activeTab === "overview" && eoi && (
              <div>
                {/* Company */}
                <SectionLabel>Company</SectionLabel>
                <InfoRow label="Company Name" value={eoi.company_name} />
                <InfoRow label="Website" value={eoi.company_website} />
                <InfoRow label="LinkedIn" value={eoi.linkedin_url} />
                <InfoRow label="Address" value={eoi.address} />

                {/* Job */}
                <SectionLabel>Job</SectionLabel>
                <InfoRow label="Designation(s)" value={eoi.job_designation?.join(", ")} />
                <InfoRow label="Employment Type" value={eoi.employment_type} />
                <InfoRow label="Work Location" value={eoi.work_location} />
                <InfoRow label="Applicable Branches" value={eoi.applicable_branches} />

                {/* Compensation */}
                <SectionLabel>Compensation</SectionLabel>
                <InfoRow label="Stipend" value={eoi.stipend} />
                <InfoRow label="CTC" value={eoi.ctc} />
                <InfoRow label="SLP Duration" value={eoi.slp_duration} />
                <InfoRow label="Other Benefits" value={eoi.other_benefits} />
                <InfoRow label="Bond" value={eoi.bond} />

                {/* Eligibility */}
                <SectionLabel>Eligibility</SectionLabel>
                <InfoRow label="CGPA" value={eoi.eligibility_cgpa} />
                <InfoRow label="Backlogs" value={eoi.eligibility_backlogs} />
                <InfoRow label="Other" value={eoi.eligibility_other} />

                {/* Descriptions */}
                <SectionLabel>Descriptions</SectionLabel>
                <InfoRow label="About Company" value={eoi.about_company} />
                <InfoRow label="Job Description" value={eoi.job_description} />

                {/* Process */}
                <SectionLabel>Process</SectionLabel>
                <div className="py-1.5 border-b border-zinc-800/50">
                  <span className="text-[11px] text-zinc-500 w-32 inline-block pt-0.5">Selection Process</span>
                  {eoi.selection_process && eoi.selection_process.length > 0 ? (
                    <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1">
                      {eoi.selection_process.map((round, i) => (
                        <span key={i} className="flex items-center gap-1 text-[11px] text-zinc-300">
                          <span className="text-zinc-600 font-mono">{i + 1}.</span> {round}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-[12px] text-zinc-600 italic">—</span>
                  )}
                </div>
                <InfoRow label="Deadline" value={state.deadline} />

                {/* Assignment */}
                <SectionLabel>Assignment</SectionLabel>
                <div className="flex items-start gap-2 py-1.5 border-b border-zinc-800/50">
                  <span className="text-[11px] text-zinc-500 w-32 flex-shrink-0 pt-0.5">Required</span>
                  {eoi.assignment_required ? (
                    <Badge color="amber">Yes — Assignment Required</Badge>
                  ) : (
                    <span className="text-[12px] text-zinc-600 italic">No</span>
                  )}
                </div>
                <InfoRow label="Deadline" value={eoi.assignment_deadline} />
                {eoi.assignment_link ? (
                  <div className="flex items-start gap-2 py-1.5 border-b border-zinc-800/50">
                    <span className="text-[11px] text-zinc-500 w-32 flex-shrink-0 pt-0.5">Link</span>
                    <a href={eoi.assignment_link} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-indigo-400 hover:underline truncate flex-1">
                      {eoi.assignment_link}
                    </a>
                  </div>
                ) : (
                  <InfoRow label="Link" value={null} />
                )}
              </div>
            )}

            {/* ─ Form Fields tab ─ */}
            {activeTab === "form" && (
              <div>
                {state.form_fields && Array.isArray(state.form_fields) && state.form_fields.length > 0 ? (
                  <div className="space-y-2">
                    {(state.form_fields as FormFieldItem[]).map((field, i) => (
                      <div key={i}
                        className="rounded-lg border border-zinc-800/60 bg-zinc-800/20 px-3 py-2.5">
                        {/* Field header row */}
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1.5 min-w-0">
                            {field.required && (
                              <span className="text-[10px] text-rose-400 flex-shrink-0 font-bold">*</span>
                            )}
                            <span className="text-[12px] text-zinc-200 font-medium truncate">{field.label}</span>
                          </div>
                          <div className="flex items-center gap-1.5 flex-shrink-0">
                            <span className="text-[10px] text-zinc-500 font-mono">
                              {FIELD_TYPE_ICONS[field.field_type] ?? "?"}
                            </span>
                            <Badge color="violet">{field.field_type}</Badge>
                          </div>
                        </div>
                        {/* Options (for dropdown / multiple_choice / checkboxes) */}
                        {field.options && field.options.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {field.options.map((opt, j) => (
                              <span key={j}
                                className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-700/40 text-zinc-400 border border-zinc-700/40">
                                {opt}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 text-center py-6">No form fields generated yet.</p>
                )}
              </div>
            )}

            {/* ─ Links tab ─ */}
            {activeTab === "links" && (
              <div className="space-y-2">
                {state.form_link && (
                  <LinkButton
                    href={state.form_link}
                    label="Open Google Form"
                    icon={
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                        className="w-4 h-4">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    }
                  />
                )}
                {state.form_sheet_link && (
                  <LinkButton
                    href={state.form_sheet_link}
                    label="Open Response Sheet"
                    icon={
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                        className="w-4 h-4">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                      </svg>
                    }
                  />
                )}
                {state.form_drive_link && (
                  <LinkButton
                    href={state.form_drive_link}
                    label="Open Drive Folder"
                    icon={
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                        className="w-4 h-4">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                      </svg>
                    }
                  />
                )}
                {!hasFormLink && !state.form_sheet_link && !state.form_drive_link && (
                  <p className="text-xs text-zinc-500 text-center py-6">No links generated yet.</p>
                )}
                {state.raw_links && state.raw_links.length > 0 && (
                  <div className="mt-3">
                    <p className="text-[11px] text-zinc-500 uppercase tracking-wide mb-2">Links from JD</p>
                    <div className="space-y-1">
                      {state.raw_links.slice(0, 5).map((link, i) => (
                        <a key={i} href={link} target="_blank" rel="noopener noreferrer"
                          className="block text-xs text-indigo-400 hover:text-indigo-300 hover:underline truncate">
                          {link}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
