import { Link } from "react-router-dom";

export default function CustomLink({ title, linkTo }: { title: string; linkTo: string; }) {
  return (
    <Link
      className="
         inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 underline underline-offset-4 decoration-2
         transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md
         dark:text-sky-300 dark:hover:text-sky-200 dark:focus:ring-sky-300 dark:focus:ring-offset-slate-950
      "
      to={linkTo}
    >
     { title }
    </Link>
  );
}
