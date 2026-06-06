import type { ProductSchool } from "../lib/school-utils";
import { RecommendationFeed } from "./RecommendationFeed";
import type { LocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  local?: LocalSchoolState;
};

export function BuildMyListApp({ schools, caveat, local }: Props) {
  return (
    <RecommendationFeed
      schools={schools}
      caveat={caveat}
      local={local}
      title="Schools to review first"
      intro="Your Rank updates locally from applicant inputs, selected weights, cost basis, and reversible exclusions while Baseline Rank stays visible."
      limit={50}
    />
  );
}
