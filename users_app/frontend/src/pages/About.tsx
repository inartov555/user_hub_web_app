import { useTranslation } from "react-i18next";
import { LayoutTemplate } from "lucide-react";
import { useAuthStore } from "../auth/store";
import UnifiedTitle from "../components/UnifiedTitle";
import { SimpleInfoMessage } from "../components/Alerts";
import CustomLink from "../components/CustomLink";
import { Card } from "../components/card";

export default function About() {
  const { t, i18n } = useTranslation();
  const { user } = useAuthStore();

  return (
    <Card className="max-w-xl mx-auto">
      <UnifiedTitle icon={<LayoutTemplate className="h-4 w-4" />} title={t("about.aboutWebsite")} />
      <SimpleInfoMessage message={t("about.infoAboutWebsite")} />
      {!user && (
        <div className="mt-4 text-sm flex justify-between">
          <CustomLink title={t("auth.createAccount")} linkTo="/signup" />
          <CustomLink title={t("auth.login")} linkTo="/login" />
        </div>
      )}
    </Card>
  );
}
