"use client";

import React, { ChangeEvent, FormEvent, useState } from "react";

interface FormDataState {
  deadline: string;
  formtemplate: string;
  jd: File | null;
}

const Newchat = () => {
  const [formData, setFormData] = useState<FormDataState>({
    deadline: "",
    formtemplate: "Basic Template",
    jd: null,
  });

  const [graphState, setGraphState] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;

    setFormData((prev) => ({
      ...prev,
      jd: file,
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    setLoading(true);
    setGraphState(null);

    const data = new FormData();
    data.append("deadline", formData.deadline);

    if (formData.jd) {
      data.append("jd", formData.jd);
    }

    try {
      const response = await fetch("http://localhost:8000/newchat", {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        throw new Error("Failed to create chat");
      }

      const result = await response.json();

      console.log(result);

      // Display final graph state
      setGraphState(result.state);
    } catch (error) {
      console.error(error);
      alert("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "700px", margin: "40px auto" }}>
      <h2>Create New Chat</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "20px" }}>
          <label>Deadline</label>
          <br />
          <input
            type="datetime-local"
            name="deadline"
            value={formData.deadline}
            onChange={handleInputChange}
            required
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label>Form Template</label>
          <br />
          <select
            name="formtemplate"
            value={formData.formtemplate}
            onChange={handleInputChange}
          >
            <option value="Basic Template">Basic Template</option>
          </select>
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label>Upload JD</label>
          <br />
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Create Chat"}
        </button>
      </form>

      {graphState && (
        <div
          style={{
            marginTop: "30px",
            padding: "16px",
            border: "1px solid #ccc",
            borderRadius: "8px",
          }}
        >
          <h3>Final Graph State</h3>

          <pre
            style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {JSON.stringify(graphState, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default Newchat;