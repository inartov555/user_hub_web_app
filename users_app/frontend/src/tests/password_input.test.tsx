import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PasswordInput from "../components/PasswordInput";

describe("PasswordInput", () => {
  it("toggles visibility", async () => {
    render(<PasswordInput label="Password" id="pwd" value="secret" onChange={() => {}} />);
    const reveal = screen.getByRole("button");
    const input = screen.getByLabelText(/password/i, { selector: 'input' }) as HTMLInputElement;
    expect(input.type).toBe("password");
    await userEvent.click(reveal);
    expect((screen.getByLabelText(/password/i, { selector: 'input' }) as HTMLInputElement).type).toBe("text");
  });
});
