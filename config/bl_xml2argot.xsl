<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:math="http://exslt.org/math">
  <xsl:output method="text" />
     <xsl:template match="/BlastOutput/*" />
     <xsl:template match="/BlastOutput/BlastOutput_iterations">
       <xsl:for-each select="/BlastOutput/BlastOutput_iterations/Iteration">
        <xsl:variable name="qid" select="Iteration_query-def"/>
        <xsl:for-each select="Iteration_hits/Hit">
          <xsl:variable name="evalue" select="math:min(Hit_hsps/Hsp/Hsp_evalue)"/>
            <xsl:choose>
            <xsl:when test="contains($qid, ' ')">
              <xsl:value-of select="substring-before($qid, ' ')" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="$qid" />
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>&#x9;</xsl:text>
          <xsl:value-of select="Hit_id"/>
          <xsl:text>&#x9;</xsl:text>
          <xsl:value-of select="$evalue"/>
          <xsl:text>&#xa;</xsl:text>
        </xsl:for-each>
      </xsl:for-each>
  </xsl:template>
  </xsl:stylesheet>