import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FormInput from "../components/FormInput";

describe("FormInput", () => {
  it("Renders a label and shows validation message", async () => {
    const onChange = vi.fn();
    render(
      <FormInput
        label="Email"
        id="email"
        value=""
        onChange={onChange}
        placeholder="Email"
        error="Required"
      />
    );
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByText(/required/i)).toBeInTheDocument();
  });
});
